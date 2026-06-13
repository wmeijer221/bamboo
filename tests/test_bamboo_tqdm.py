from dataclasses import dataclass

import pandas as pd
import pytest
from beartype import beartype
from tqdm import tqdm

from bamboo import BambooObject, bamboo_transform
from bamboo._exception import BambooTransformationException


def test_bamboo_transform_progress_apply_with_tqdm_happy_path():
    """Verify tqdm.progress_apply works with bamboo_transform and returns the expected row output DataFrame."""

    tqdm.pandas()

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

    df = pd.DataFrame({"id": [1, 2], "name": ["alice", "bob"]})
    result = df.progress_apply(transform, axis=1)  # type: ignore

    assert isinstance(result, pd.DataFrame)
    assert result.to_dict("records") == [
        {"id": "1", "full_name": "ALICE"},
        {"id": "2", "full_name": "BOB"},
    ]


def test_bamboo_transform_progress_apply_with_tqdm_invalid_output_raises_bamboo_exception():
    """Ensure tqdm.progress_apply wraps transformation exceptions as BambooException for bamboo_transform functions."""

    tqdm.pandas()

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

    df = pd.DataFrame({"id": [1], "name": ["alice"]})

    with pytest.raises(BambooTransformationException):
        df.progress_apply(transform, axis=1)
