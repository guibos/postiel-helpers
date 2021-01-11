import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import Any, Callable, List, Dict, Optional, Union, Coroutine

import aio_pika
from aio_pika import ExchangeType, Channel, Exchange
from aio_pika.robust_connection import ConnectionType
from aio_pika.types import TimeoutType
from async_lru import alru_cache
from pydantic import validator

from postiel_helpers.action.action import Action
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


class CreateConfig(DataModel):
    queues: List[QueueConfig] = field(default_factory=list)
    exchanges: List[ExchangeConfig] = field(default_factory=list)
    bindings: Dict[str, List[str]] = field(default_factory=dict)

    @validator('bindings')
    def bindings_check(cls, bindings, values, **kwargs):
        queues = {queue_config.name for queue_config in values['queues']}
        exchanges = {exchange_config.name for exchange_config in values['exchanges']}
        for queue_name, exchange_name_list in bindings.items():
            assert queue_name in queues, f"Queue {queue_name} is not declared in queues"
            for exchange_name in exchange_name_list:
                assert exchange_name in exchanges, f"Exchange {exchange_name} is not declared in exchanges"
        return bindings


class QOS(DataModel):
    prefetch_count: int = 0
    prefetch_size: int = 0
    global_: bool = False
    timeout: TimeoutType = None


class ConsumerDead(DataModel):
    dead_exchange_name: str
    dead_routing_key: str


class Consumer(DataModel):
    qos: QOS = field(default_factory=QOS)
    queue_name: str
    consumer_name: str
    # consumer_dead: ConsumerDead


class RabbitMQConfig(DataModel):
    common: RabbitMQCommonConfig
    connection: RabbitMQConnectionConfig
    create: CreateConfig = field(default_factory=CreateConfig)
    consumer: List[Consumer] = field(default_factory=list)


class RabbitMQ(MessageBrokerInterface):
    def __init__(self, connection: ConnectionType, default_channel: Channel, common_config: RabbitMQCommonConfig,
                 consumer_config: List[Consumer], consumer_functions: Dict[str, Coroutine]):
        super().__init__()
        self._logger = logging.getLogger(common_config.logger_name)
        self._connection = connection
        self._default_channel = default_channel
        self._consumers: List[ConsumerData] = []
        self._consumer_config = consumer_config
        self._consumer_functions=consumer_functions

    @classmethod
    async def initialize(cls, config: Dict[str, Any], consumers_functions: Dict[str, Coroutine] = field(default_factory=dict)):
        config = RabbitMQConfig.parse_obj(config)
        connection = await aio_pika.connect_robust(**config.connection.dict())
        default_channel = await connection.channel()

        await cls._declare_config(default_channel, config.create)
        consumers = await cls._create_consumers(
            consumer_config=config.consumer,
            connection=connection,
            consumers_functions=consumers_functions)
        instance = cls(connection=connection, default_channel=default_channel, common_config=config.common, consumers)

        return instance

    async def _create_consumers(self):
        async def _get_consumer_tag() -> str:
            return uuid.uuid4().hex

        async def _process_message(func: Callable,  consumer_dead: ConsumerDead, message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    await func(message.body)
                except Exception:
                    pass

        consumers = []

        for consumer_config in self._consumer_config:
            channel = await self._connection.channel()
            await channel.set_qos(**consumer_config.qos.dict())
            consumer_queue = await channel.get_queue(consumer_config.queue_name)
            consumer_tag = await _get_consumer_tag()
            partial_function = partial(_process_message, self._consumer_functions[consumer_config.consumer_name], self._consumer_config.consumer_dead)
            task = asyncio.create_task(
                consumer_queue.consume(
                    partial_function,
                    consumer_tag=consumer_tag,
                )
            )

            self._consumers.append(
                ConsumerData(
                    queue=consumer_queue,
                    consumer_tag=consumer_tag,
                    task=task,
                    channel=channel
                )
            )

    @staticmethod
    async def _declare_config(channel: Channel, create_config: CreateConfig) -> None:
        queues = [channel.declare_queue(**queue_config.dict())
                  for queue_config in create_config.queues]
        exchanges = [channel.declare_exchange(**exchange_config.dict())
                     for exchange_config in create_config.exchanges]

        queues = await asyncio.gather(*queues)
        await asyncio.gather(*exchanges)

        queues = {queue.name: queue for queue in queues}

        bindings = []
        for queue_name, exchange_name_list in create_config.bindings.items():
            queue = queues[queue_name]
            for exchange_name in exchange_name_list:
                bindings.append(queue.bind(exchange_name))

        await asyncio.gather(*bindings)

    @staticmethod
    async def _get_delay(publish_datetime: datetime) -> float:
        timedelta = publish_datetime - datetime.now()
        return timedelta.total_seconds() * 1000

    async def send_message(self, message: Message) -> None:
        headers = {}
        if message.publish_datetime:
            headers['x-delay'] = await self._get_delay(message.publish_datetime)

        exchange = await self._get_exchange(message.exchange_name)

        await exchange.publish(
            aio_pika.Message(
                headers=headers,
                body=message.action.serialize()),
            routing_key=message.routing_key,
        )

    @alru_cache
    async def _get_exchange(self, exchange_name: str) -> Exchange:
        return await self._default_channel.get_exchange(exchange_name)

    async def close(self) -> None:
        cancel_consumers = [consumer.queue.cancel(consumer_tag=consumer.consumer_tag) for consumer in self._consumers]
        await asyncio.gather(*cancel_consumers)

        self._logger.debug('Sleep grace.')
        await asyncio.sleep(20)

        close_channels = [consumer.channel.close() for consumer in self._consumers]
        await asyncio.gather(*close_channels)

        await self._connection.close()
