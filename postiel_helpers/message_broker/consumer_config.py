from collections import Coroutine
from dataclasses import dataclass

from postiel_helpers.action.action import Action


@dataclass
class ConsumerConfig:
    func: Coroutine
    action: Action
