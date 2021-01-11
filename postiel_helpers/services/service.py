import asyncio
import os
import signal
from abc import abstractmethod, ABCMeta
from typing import Any, Dict, Callable

import aiofiles
import yaml
from pydantic import ValidationError

from postiel_helpers.abstract.attribute import AbstractAttribute
from postiel_helpers.config.base_config import BaseConfig
from postiel_helpers.config.message_broker import MessageBrokerConfig
from postiel_helpers.message_broker.interface import MessageBrokerInterface
from postiel_helpers.message_broker.rabbitmq.rabbitmq import RabbitMQ
from postiel_helpers.services.logger import LoggerMixin


class Service(LoggerMixin, metaclass=ABCMeta):
    _CONFIG = BaseConfig
    _CONFIG_DIRECTORY = AbstractAttribute()
    _CONFIG_FILENAME = AbstractAttribute()
    _MESSAGE_BROKERS_CLASSES: Dict[str, MessageBrokerInterface] = {
        'RabbitMQ': RabbitMQ
    }

    def __init__(self):
        self._config_loaded = False
        self._brokers: Dict[str, MessageBrokerInterface] = {}
        self._consumer_functions: Dict[str, Callable] = {}
        super().__init__()

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGHUP, self._create_load_config_task)
        loop.run_until_complete(self._load_config())
        if not self._config_loaded:
            raise RuntimeError("Config not loaded")
        loop.run_until_complete(self._start())
        loop.run_until_complete(self._stop())

    def _create_load_config_task(self) -> None:
        asyncio.create_task(self._load_config())

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError()

    async def _load_config(self) -> None:
        data = await self._get_config_data()
        try:
            config = self._CONFIG.parse_obj(data)
        except ValidationError as err:
            self._logger.error(err)
            return

        await self._load_logger_config(config.logging)

        await self._load_brokers(config.message_brokers)

        self._config_loaded = True
        self._logger.info('Config loaded')

    async def _load_brokers(self, message_brokers: Dict[str, MessageBrokerConfig]) -> None:
        brokers = {
            name: await self._MESSAGE_BROKERS_CLASSES[config.class_name].initialize(
                config=config.config, consumers_functions=self._consumer_functions)
            for name, config in message_brokers.items()
        }  # TODO: Improve performance
        self._brokers = brokers

    async def _get_config_data(self) -> Dict[str, Any]:
        async with aiofiles.open(os.path.join(self._CONFIG_DIRECTORY, self._CONFIG_FILENAME), mode='r') as f:
            data = await f.read()
        return yaml.load(data, Loader=yaml.FullLoader)
