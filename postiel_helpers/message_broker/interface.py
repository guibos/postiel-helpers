from abc import abstractmethod, ABCMeta
from typing import Any, Dict, Callable, Optional

from postiel_helpers.message_broker.message import Message
from postiel_helpers.model.field import field


class MessageBrokerInterface(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    async def initialize(cls, config: Dict[str, Any], consumers_functions: Dict[str, Callable] = field(default_factory=dict)):
        raise NotImplementedError()

    @abstractmethod
    async def send_message(self, message: Message) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()
