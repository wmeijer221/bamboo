from dataclasses import dataclass

import pandas as pd
import pytest

from bamboo import BambooObject, bamboo_transform
from bamboo._exception import BambooInputException, BambooOutputException, BambooTransformationException


def test_bamboo_transform_infers_input_and_output_types():
    """Verify decorator inference of input and output Bamboo types when explicit types are omitted."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

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


def test_bamboo_transform_with_explicit_input_and_output_types():
    """Verify bamboo_transform behavior when InputType and OutputType are explicitly provided."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @dataclass(kw_only=True)
    class PersonOutput(BambooObject):
        id: str
        full_name: str

    @bamboo_transform(InputType=Person, OutputType=PersonOutput)
    def transform(person):
        return PersonOutput(id=str(person.id), full_name=person.name.title())

    row = pd.Series({"id": 2, "name": "bob"})
    output = transform(row)

    assert isinstance(output, pd.Series)
    assert output.to_dict() == {"id": "2", "full_name": "Bob"}
    assert list(output.index) == ["id", "full_name"]


def test_bamboo_transform_input_type_underspecified_for_row_data_raises_bamboo_exception():
    """Validate that underspecified input row schema raises BambooException during transformation."""

    @dataclass(kw_only=True)
    class InputModel(BambooObject):
        id: int

    @dataclass(kw_only=True)
    class OutputModel(BambooObject):
        id: int

    @bamboo_transform
    def transform(model: InputModel) -> OutputModel:
        return OutputModel(id=model.id)

    row = pd.Series({"id": 1, "name": "alice"})

    with pytest.raises(BambooInputException):
        transform(row)


def test_bamboo_transform_input_type_overspecified_for_row_data_raises_bamboo_exception():
    """Validate that overspecified input schema with missing row columns raises BambooException."""

    @dataclass(kw_only=True)
    class InputModel(BambooObject):
        id: int
        name: str

    @dataclass(kw_only=True)
    class OutputModel(BambooObject):
        id: int
        name: str

    @bamboo_transform
    def transform(model: InputModel) -> OutputModel:
        return OutputModel(id=model.id, name=model.name)

    row = pd.Series({"id": 1})

    with pytest.raises(BambooInputException):
        transform(row)


def test_bamboo_transform_wraps_transformation_exceptions_as_bamboo_exception():
    """Ensure that exceptions inside the transformation function are wrapped as BambooException."""

    @dataclass(kw_only=True)
    class InputModel(BambooObject):
        id: int

    @dataclass(kw_only=True)
    class OutputModel(BambooObject):
        id: int

    @bamboo_transform
    def transform(model: InputModel) -> OutputModel:
        raise ValueError("boom")

    row = pd.Series({"id": 1})

    with pytest.raises(BambooTransformationException):
        transform(row)


def test_bamboo_transform_supports_inherited_dataclasses():
    """Confirm bamboo_transform works when the output type is an inherited BambooObject dataclass."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @dataclass(kw_only=True)
    class PersonWithAge(Person):
        age: int

    @bamboo_transform
    def transform(person: Person) -> PersonWithAge:
        return PersonWithAge(id=person.id, name=person.name, age=30)

    row = pd.Series({"id": 3, "name": "carol"})
    output = transform(row)

    assert isinstance(output, pd.Series)
    assert output.to_dict() == {"id": 3, "name": "carol", "age": 30}
    assert list(output.index) == ["id", "name", "age"]


def test_bamboo_transform_can_remove_columns_using_none_type_on_inherited_dataclass():
    """Verify that output dataclass fields annotated as None are omitted from the result series."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str
        favorite_color: str

    @dataclass(kw_only=True)
    class PersonWithoutColor(Person):
        favorite_color: None = None

    @bamboo_transform
    def transform(person: Person) -> PersonWithoutColor:
        return PersonWithoutColor(id=person.id, name=person.name)

    row = pd.Series({"id": 4, "name": "dana", "favorite_color": "green"})
    output = transform(row)

    assert isinstance(output, pd.Series)
    assert output.to_dict() == {"id": 4, "name": "dana"}
    assert list(output.index) == ["id", "name"]


@pytest.mark.parametrize("violating_id", [0, 25, 49])
def test_bamboo_transform_dataframe_row_with_none_output_type_raises_bamboo_exception(violating_id: int):
    """Verify that a DataFrame with a single invalid first row raises BambooException."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @dataclass(kw_only=True)
    class ReturnType(BambooObject):
        id: str
        name: str

    @bamboo_transform
    def transform(person: Person) -> ReturnType:
        if person.id == violating_id:
            # This is intentionally the wrong type.
            return None  # type: ignore
        return ReturnType(id=str(person.id), name=person.name)

    df = pd.DataFrame({"id": list(range(50)), "name": [f"person_{i}" for i in range(50)]})

    with pytest.raises(BambooOutputException):
        df.apply(transform, axis=1)


@pytest.mark.parametrize("violating_id", [0, 25, 49])
def test_bamboo_transform_dataframe_row_violates_output_type_raises_bamboo_exception(violating_id: int):
    """Verify that a DataFrame with a single invalid first row raises BambooException."""

    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str

    @dataclass(kw_only=True)
    class ReturnType(BambooObject):
        id: str
        name: str

    @bamboo_transform
    def transform(person: Person) -> ReturnType:
        if person.id == violating_id:
            # This is intentionally the wrong type.
            return Person(id=person.id, name=person.name)  # type: ignore
        return ReturnType(id=str(person.id), name=person.name)

    df = pd.DataFrame({"id": list(range(50)), "name": [f"person_{i}" for i in range(50)]})

    with pytest.raises(BambooOutputException):
        df.apply(transform, axis=1)
