from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Post:
    """Post"""
    post_id: Optional[Union[str, int]] = None
    # title: Optional[RichText] = None
    # description: Optional[RichText] = None
    # start_at: Optional[datetime] = None
    # end_at: Optional[datetime] = None
    # url: Optional[str] = None
    # files: List[FileValueObject] = field(default_factory=list)
    # author: Optional[Author] = None
    # custom_fields: List[CustomField] = field(default_factory=list)