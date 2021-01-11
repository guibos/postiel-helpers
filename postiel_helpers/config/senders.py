from typing import List


from postiel_helpers.config.channel import ChannelConfig
from postiel_helpers.config.queue import QueueConfig
from postiel_helpers.model.data import DataModel


class SenderConfig(DataModel):
    channels: List[ChannelConfig]
    queue_config: QueueConfig

