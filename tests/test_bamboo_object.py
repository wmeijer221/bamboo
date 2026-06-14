from dataclasses import dataclass

import pandas as pd

from bamboo import BambooObject


def test_bamboo_object_returns_attribute_values_before_represented_row_is_set():
    """Confirm BambooObject returns stored attribute values before a represented row is bound."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    person = Person(id=1, name="alice")

    assert person.id == 1
    assert person.name == "alice"
