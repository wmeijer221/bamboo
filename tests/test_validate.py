from dataclasses import dataclass

import pandas as pd
import pytest

from bamboo import BambooObject, validate
from bamboo._exception import BambooException


def test_validate_happy_path():
    """Verify that validate passes when DataFrame exactly matches the BambooObject type."""

    @dataclass(kw_only=True)
    class Row(BambooObject):
        a: int
        b: str

    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    # Should not raise
    validate(df, Row)


def test_validate_underspecified():
    """Verify that validate raises BambooException when DataFrame is missing required columns."""

    @dataclass(kw_only=True)
    class Row(BambooObject):
        a: int
        b: str
        c: float

    # Missing column 'c'
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    with pytest.raises(BambooException):
        validate(df, Row)


def test_validate_overspecified():
    """Verify that validate raises BambooException when DataFrame has extra columns not in the BambooObject."""

    @dataclass(kw_only=True)
    class Row(BambooObject):
        a: int
        b: str

    # Extra column 'd' not in Row
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"], "d": [1.0, 2.0]})

    with pytest.raises(BambooException):
        validate(df, Row)
