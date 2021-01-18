from abc import abstractmethod, ABCMeta
from typing import Any, Dict, Callable

from postiel_helpers.message_broker.message import Message


class MessageBrokerInterface(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    async def initialize(cls, config: Dict[str, Any], service_consumers: Dict[str, Callable], close_grace: int):
        raise NotImplementedError()

    @abstractmethod
    async def send_message(self, message: Message) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def load_failed(self) -> None:
        raise NotImplementedError()

