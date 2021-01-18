from datetime import datetime
from typing import Optional, Dict, Any

from postiel_helpers.action.action import Action
from postiel_helpers.model.data import DataModel


class Message(DataModel):
    action: Action
    routing_config: Dict[str, Any]
    publish_datetime: Optional[datetime] = None


