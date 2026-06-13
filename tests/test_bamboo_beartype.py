from dataclasses import dataclass

import pandas as pd
import pytest
from beartype import beartype

from bamboo import BambooObject, bamboo_transform
from bamboo._exception import BambooException


def test_bamboo_transform_with_beartype_output_violation_raises_bamboo_exception():
    """Ensure a beartype-annotated BambooObject output with an invalid value raises BambooException."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @beartype
    @dataclass(kw_only=True)
    class PersonOutput(BambooObject):
        id: str
        full_name: str

    @bamboo_transform
    def transform(person: Person) -> PersonOutput:
        # We ignore the linter error here, as the type is intentionally wrong.
        return PersonOutput(id=person.id, full_name=person.name.upper())  # type: ignore

    row = pd.Series({"id": 1, "name": "alice"})

    with pytest.raises(BambooException):
        transform(row)


def test_bamboo_transform_with_beartype_output_ok():
    """Verify a valid beartype-annotated BambooObject output passes and returns the expected series."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @beartype
    @dataclass(kw_only=True)
    class PersonOutput(BambooObject):
        id: str
        full_name: str

    @bamboo_transform
    def transform(person: Person) -> PersonOutput:
        return PersonOutput(id=str(person.id), full_name=person.name.upper())

    row = pd.Series({"id": 1, "name": "alice"})
    output = transform(row)

    assert isinstance(output, pd.Series)
    assert output.to_dict() == {"id": "1", "full_name": "ALICE"}
    assert list(output.index) == ["id", "full_name"]
