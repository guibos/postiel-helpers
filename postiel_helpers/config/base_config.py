from typing import Optional, Dict, Any

from postiel_helpers.config.logging import LoggingConfig
from postiel_helpers.config.message_broker import MessageBrokerConfig
from postiel_helpers.model.data import DataModel
from postiel_helpers.model.field import field


class BaseConfig(DataModel):
    logging: Optional[LoggingConfig] = None
    message_brokers: Dict[str, MessageBrokerConfig] = field(default_factory=dict)
    # senders_config: List[SenderConfig]
