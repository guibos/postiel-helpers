from typing import List, Union

from postiel_helpers.action.action import Action
from postiel_helpers.action.post.post import Post


class PostAction(Action):
    channels: List[Union[str, int]]
    posts: List[Post]
