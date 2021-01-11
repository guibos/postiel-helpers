from collections import OrderedDict
from datetime import datetime
from typing import Any
import typing

import pytest
from pydantic import BaseModel, ValidationError

from postiel_helpers.langauge.language import Language
from postiel_helpers.model.data import DataModel


class DataInner(DataModel):
    type_datetime: datetime


class Data(BaseModel):
    type_integer: int
    type_float: float
    type_string: str
    type_datetime: datetime
    type_data_inner: DataInner
    type_bytes: bytes
    type_language: Language
    type_ordered_dict: typing.OrderedDict[Any, Any]


def test_integrity_ok():
    data = Data(
        type_integer=1,
        type_float=1.1,
        type_string='1',
        type_datetime=datetime.now(),
        type_data_inner=DataInner(type_datetime=datetime.now()),
        type_bytes=b'Espa\xc3\xb1a',
        type_language=Language.ES,
        type_ordered_dict=OrderedDict([(Language.ES, 'a')])
    )


def test_integrity_fail():
    with pytest.raises(ValidationError):
        data = Data(
            type_integer='a',
            type_float=1.1,
            type_string='1',
            type_datetime=datetime.now(),
            type_data_inner=DataInner(type_datetime=datetime.now()),
            type_bytes=b'Espa\xc3\xb1a',
            type_language=Language.ES,
            type_ordered_dict=OrderedDict([(Language.ES, 'a')])
        )
