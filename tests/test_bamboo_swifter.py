from dataclasses import dataclass

import pandas as pd
import pytest
import swifter
from beartype import beartype

from bamboo import BambooObject, bamboo_transform, validate
from bamboo._exception import BambooException


def test_bamboo_transform_swifter_force_parallel_threads_happy_path():
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

    n = 100
    df = pd.DataFrame({"id": list(range(n)), "name": ["alice"] * n})
    result = df.swifter.force_parallel().set_dask_scheduler("threads").apply(transform, axis=1)

    assert isinstance(result, pd.DataFrame)
    assert result.to_dict("records") == [
        {"id": str(i), "full_name": "ALICE"} for i in range(n)
    ]


def test_bamboo_transform_swifter_force_parallel_threads_dataset_integrity_is_preserved():
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

    n = 100
    df = pd.DataFrame({"id": list(range(n)), "name": ["alice"] * n})
    result = df.swifter.force_parallel().set_dask_scheduler("threads").apply(transform, axis=1)

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (n, 2)
    assert list(result.columns) == ["id", "full_name"]
    validate(result, PersonOutput)
    assert result.to_dict("records") == [
        {"id": str(i), "full_name": "ALICE"} for i in range(n)
    ]


def test_bamboo_transform_swifter_force_parallel_threads_invalid_output_raises_bamboo_exception():
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
        raise ValueError("boom")

    n = 100
    df = pd.DataFrame({"id": list(range(n)), "name": ["alice"] * n})

    with pytest.raises(BambooException):
        df.swifter.force_parallel().set_dask_scheduler("threads").apply(transform, axis=1)
