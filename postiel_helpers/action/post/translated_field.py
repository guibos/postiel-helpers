from dataclasses import dataclass
from typing import Any


@dataclass
class TranslatedField:
    field_name: str
    mimetype: str
    data: Any
