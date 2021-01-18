from dataclasses import dataclass
from typing import Awaitable, Type, Callable

from postiel_helpers.action.action import Action


@dataclass
class ServiceConsumer:
    func: Callable[[Type[Action]], Awaitable[None]]
    action_type: Type[Action]
