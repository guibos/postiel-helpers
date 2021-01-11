from datetime import datetime
from typing import Union, Optional

from postiel_helpers.action.action import Action
from postiel_helpers.model.data import DataModel


class Message(DataModel):
    action: Action
    routing_key: str
    exchange_name: str
    publish_datetime: Optional[datetime] = None


