from abc import ABCMeta

import pytest

from postiel_helpers.abstract.attribute import AbstractAttribute


class Base(metaclass=ABCMeta):
    ABSTRACT_ATTRIBUTE = AbstractAttribute()


def test_abstract_attribute_no_inheritance():
    with pytest.raises(TypeError):
        Base()


def test_abstract_attribute_inheritance():
    class Children(Base):
        pass

    with pytest.raises(TypeError):
        Children()


def test_abstract_attribute():
    class Children(Base):
        ABSTRACT_ATTRIBUTE = 1

    Children()
