import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import Any, Callable, List, Dict, Optional, Union

import aio_pika
from aio_pika import ExchangeType, Channel, Exchange, Queue
from aio_pika.robust_connection import ConnectionType
from aio_pika.types import TimeoutType
from async_lru import alru_cache
from pydantic import validator

from postiel_helpers.action.action import Action
from postiel_helpers.message_broker.service_consumer import ServiceConsumer
from postiel_helpers.message_broker.interface import MessageBrokerInterface

from postiel_helpers.message_broker.message import Message
from postiel_helpers.model.data import DataModel
from postiel_helpers.model.field import field


@dataclass
class ConsumerData:
    channel: Channel
    queue: aio_pika.Queue
    consumer_tag: str
    task: asyncio.Task


class RabbitMQConnectionConfig(DataModel):
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 5672
    login: str = "guest"
    password: str = "guest"
    virtualhost: str = "/"
    ssl: bool = False
    ssl_options: Optional[dict] = None
    timeout: Optional[TimeoutType] = None
    client_properties: Optional[dict] = None


class RabbitMQCommonConfig(DataModel):
    logger_name: str


class QueueConfig(DataModel):
    name: str = None
    durable: bool = None
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: dict = None
    timeout: TimeoutType = None


class ExchangeConfig(DataModel):
    name: str
    type: Union[ExchangeType, str] = ExchangeType.DIRECT
    durable: bool = None
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: dict = None
    timeout: TimeoutType = None


class BindingConfig(DataModel):
    queue_name: str
    exchange_name: str
    routing_key: str = ''


class CreateConfig(DataModel):
    queues: List[QueueConfig] = field(default_factory=list)
    exchanges: List[ExchangeConfig] = field(default_factory=list)
    bindings: List[BindingConfig] = field(default_factory=list)

    @validator('bindings')
    def bindings_check(cls, bindings, values, **kwargs):
        queues = {queue_config.name for queue_config in values['queues']}
        exchanges = {exchange_config.name for exchange_config in values['exchanges']}
        for binding in bindings:
            assert binding.queue_name in queues, f"Queue {binding.queue_name} is not declared in queues"
            assert binding.exchange_name in exchanges, f"Exchange {binding.exchange_name} is not declared in exchanges"
        return bindings


class QOS(DataModel):
    prefetch_count: int = 0
    prefetch_size: int = 0
    global_: bool = False
    timeout: TimeoutType = None


class RoutingConfig(DataModel):
    routing_key: str
    exchange_name: str


class ConsumerConfig(DataModel):
    qos: QOS = field(default_factory=QOS)
    queue_name: str
    consumer_name: str
    failed_message_routing: Optional[RoutingConfig] = None


class RabbitMQConfig(DataModel):
    common: RabbitMQCommonConfig
    connection: RabbitMQConnectionConfig
    create: CreateConfig = field(default_factory=CreateConfig)
    consumers: List[ConsumerConfig] = field(default_factory=list)
    failed_consumers: List[ConsumerConfig] = field(default_factory=list)

    @validator('consumers')
    def check_failed_message_routing(cls, consumers, values):
        exchange_names = [exchange.name for exchange in values['create'].exchanges]
        for consumer in consumers:
            assert consumer.failed_message_routing.exchange_name in exchange_names
        return consumers


class RabbitMQ(MessageBrokerInterface):
    def __init__(self, connection: ConnectionType, default_channel: Channel, common_config: RabbitMQCommonConfig,
                 service_consumers: Dict[str, ServiceConsumer], close_grace: int):
        super().__init__()
        self._logger = logging.getLogger(common_config.logger_name)
        self._connection = connection
        self._default_channel = default_channel
        self._consumers: List[ConsumerData] = []
        self._service_consumers = service_consumers
        self._close_grace = close_grace

    @classmethod
    async def initialize(cls, config: Dict[str, Any],
                         service_consumers: Dict[str, ServiceConsumer],
                         close_grace: int):
        async def check_consumer_name_available(consumers: List[ConsumerConfig], service_consumers: Dict[str, ServiceConsumer]):
            for consumer in consumers:
                assert consumer.consumer_name in service_consumers, f"Consumer {consumer.consumer_name} " \
                                                                    f"is not available."

        config = RabbitMQConfig.parse_obj(config)
        await check_consumer_name_available(config.consumers, service_consumers)
        await check_consumer_name_available(config.failed_consumers, service_consumers)

        connection = await aio_pika.connect_robust(**config.connection.dict())
        default_channel = await connection.channel()

        await cls._declare_config(default_channel, config.create)
        instance = cls(connection=connection,
                       default_channel=default_channel,
                       common_config=config.common,
                       service_consumers=service_consumers,
                       close_grace=close_grace
                       )
        await instance.create_consumers(config.consumers)

        return instance

    @staticmethod
    async def _get_consumer_tag() -> str:
        return uuid.uuid4().hex

    async def _process_message(self, func: Callable, action_type: Action, failed_routing_config: Optional[RoutingConfig],
                               message: aio_pika.IncomingMessage,
                               ) -> None:
        async with message.process():
            action = action_type.deserialize(message.body)
            try:
                await func(action)
            except Exception:
                self._logger.exception("Unexpected error, on message processing.")
                if failed_routing_config:
                    failed_message = Message(
                        action=action,
                        routing_config=failed_routing_config.dict()
                    )
                    await self.send_message(failed_message)

                else:
                    self._logger.debug("Error detected but no failed routing config loaded. Message will be discarded.")

    async def load_failed(self) -> None:
        pass

    async def create_consumers(self, consumers_config: List[ConsumerConfig]):
        self._consumers = await asyncio.gather(
            *[self._create_consumer(consumer_config) for consumer_config in consumers_config])

    async def _create_consumer(self, consumer_config: ConsumerConfig) -> ConsumerData:
        channel = await self._connection.channel()
        await channel.set_qos(**consumer_config.qos.dict())
        consumer_queue = await channel.get_queue(consumer_config.queue_name)
        consumer_tag = await self._get_consumer_tag()
        consumer_service_config = self._service_consumers[consumer_config.consumer_name]
        partial_function = partial(
            self._process_message,
            consumer_service_config.func,
            consumer_service_config.action_type,
            consumer_config.failed_message_routing
        )
        task = asyncio.create_task(
            consumer_queue.consume(
                partial_function,
                consumer_tag=consumer_tag,
            )
        )

        return ConsumerData(
            queue=consumer_queue,
            consumer_tag=consumer_tag,
            task=task,
            channel=channel
        )

    @staticmethod
    async def _declare_config(channel: Channel, create_config: CreateConfig) -> None:
        queues = [channel.declare_queue(**queue_config.dict())
                  for queue_config in create_config.queues]
        exchanges = [channel.declare_exchange(**exchange_config.dict())
                     for exchange_config in create_config.exchanges]

        queue_list = await asyncio.gather(*queues)
        await asyncio.gather(*exchanges)

        queues_dict: Dict[str, Queue] = {queue.name: queue for queue in queue_list}

        bindings = [queues_dict[binding.queue_name].bind(
            exchange=binding.exchange_name, routing_key=binding.routing_key) for binding in create_config.bindings]

        await asyncio.gather(*bindings)

    @staticmethod
    async def _get_delay(publish_datetime: datetime) -> float:
        timedelta = publish_datetime - datetime.now()
        return timedelta.total_seconds() * 1000

    async def send_message(self, message: Message) -> None:
        routing_config = RoutingConfig.parse_obj(message.routing_config)
        headers = {}
        if message.publish_datetime:
            headers['x-delay'] = await self._get_delay(message.publish_datetime)

        exchange = await self._get_exchange(routing_config.exchange_name)

        await exchange.publish(
            aio_pika.Message(
                headers=headers,
                body=message.action.serialize()),
            routing_key=routing_config.routing_key,
        )

    @alru_cache
    async def _get_exchange(self, exchange_name: str) -> Exchange:
        return await self._default_channel.get_exchange(exchange_name)

    async def close(self) -> None:
        cancel_consumers = [consumer.queue.cancel(consumer_tag=consumer.consumer_tag) for consumer in self._consumers]
        await asyncio.gather(*cancel_consumers)

        self._logger.debug('Waiting close grace %s seconds', self._close_grace)
        await asyncio.sleep(self._close_grace)

        close_channels = [consumer.channel.close() for consumer in self._consumers]
        await asyncio.gather(*close_channels)

        await self._connection.close()
