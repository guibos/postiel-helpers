from typing import Union, List


from postiel_helpers.model.data import DataModel


class MoveUsersAction(DataModel):
    channel: Union[str, int]
    users: List[Union[str, int]]
