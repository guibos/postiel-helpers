from collections import OrderedDict
import typing
from typing import Optional, Union, List

from postiel_helpers.action.post.author import Author
from postiel_helpers.action.post.multi_language_field import MultiLanguageField
from postiel_helpers.model.data import DataModel
from postiel_helpers.action.post.file_object import FileObject
from postiel_helpers.model.field import field


class Post(DataModel):
    """Post"""
    channel_destination: List[Union[str, int]]
    post_id: Optional[Union[str, int]] = None
    author: Optional[Author] = None
    template: Optional[str] = None
    data: typing.OrderedDict[str, MultiLanguageField] = field(default_factory=OrderedDict)
    files: typing.OrderedDict[str, FileObject] = field(default_factory=OrderedDict)

