"""Example: default usage with type hints.

Define a Bamboo row type with dataclasses and annotate the transform function
so `@bamboo_transform` can infer input/output types.
"""
from dataclasses import dataclass
import pandas as pd

from bamboo import BambooObject, bamboo_transform, validate


@dataclass
class InputRow(BambooObject):
    a: int
    b: int


@dataclass
class OutputRow(BambooObject):
    a: int
    b: int


@bamboo_transform
def inc_and_double(row: InputRow) -> OutputRow:
    return OutputRow(a=row.a + 1, b=row.b * 2)


def demo():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
    validate(df, InputRow)
    print("input:\n", df)
    print("transformed:\n", df.apply(inc_and_double, axis=1))


if __name__ == "__main__":
    demo()
