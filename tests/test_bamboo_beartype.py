from dataclasses import dataclass

import pandas as pd
import pytest
from beartype import beartype

from bamboo import BambooObject, bamboo_transform
from bamboo._exception import BambooTransformationException


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
        return PersonOutput(id=person.id, full_name=person.name)  # type: ignore

    row = pd.Series({"id": 1, "name": "alice"})

    with pytest.raises(BambooTransformationException):
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


@pytest.mark.parametrize("violating_id", [0, 25, 49])
def test_bamboo_transform_input_type_overspecified_for_row_data_raises_bamboo_exception(violating_id: int):
    """Validate that overspecified input schema with missing row columns raises BambooException."""

    @beartype
    @dataclass(kw_only=True)
    class InputModel(BambooObject):
        id: int
        name: str

    @beartype
    @dataclass(kw_only=True)
    class OutputModel(BambooObject):
        id: str
        name: str

    @bamboo_transform
    def transform(model: InputModel) -> OutputModel:
        if model.id == violating_id:
            # This is intentionally wrong.
            return OutputModel(id=model.id, name=model.name)  # type: ignore
        return OutputModel(id=str(model.id), name=model.name)

    df = pd.DataFrame({"id": list(range(50)), "name": [f"person_{i}" for i in range(50)]})

    with pytest.raises(BambooTransformationException):
        df.apply(transform, axis=1)
