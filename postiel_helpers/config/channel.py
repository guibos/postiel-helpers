from typing import Union


from postiel_helpers.model.data import DataModel


class ChannelConfig(DataModel):
    id: Union[str, int]
    #post_data: Post
