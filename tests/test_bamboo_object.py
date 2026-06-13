from dataclasses import dataclass

import pandas as pd

from bamboo import BambooObject


def test_bamboo_object_returns_attribute_values_before_represented_row_is_set():
    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    person = Person(id=1, name="alice")

    assert person.id == 1
    assert person.name == "alice"


def test_bamboo_object_returns_represented_row_values_after_represented_row_is_set():
    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    person = Person(id=1, name="alice")
    row = pd.Series({"id": 2, "name": "bob"})
    person._set_represented_row(row)

    assert person.id == 2
    assert person.name == "bob"
    assert person.id != 1
    assert person.name != "alice"


def test_bamboo_object_switches_values_before_and_after_setting_represented_row():
    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    person = Person(id=1, name="alice")

    assert person.id == 1
    assert person.name == "alice"

    row = pd.Series({"id": 2, "name": "bob"})
    person._set_represented_row(row)

    assert person.id == 2
    assert person.name == "bob"
    assert person.id != 1
    assert person.name != "alice"


def test_bamboo_object_resets_represented_row_to_none():
    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    person = Person(id=1, name="alice")
    row = pd.Series({"id": 2, "name": "bob"})

    assert person.id == 1
    assert person.name == "alice"

    person._set_represented_row(row)
    assert person.id == 2
    assert person.name == "bob"

    person._set_represented_row(None)
    assert person.id == 1
    assert person.name == "alice"
