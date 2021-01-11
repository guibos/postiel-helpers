from typing import Any, Dict

from pydantic.main import BaseModel


class MessageBrokerConfig(BaseModel):
    class_name: str
    config: Dict[str, Any]
