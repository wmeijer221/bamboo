"""Example: default usage without type hints (parameterized decorator).

When you don't want to use type hints on the function, pass `InputType` and
`OutputType` explicitly to `@bamboo_transform`.
"""
from dataclasses import dataclass
import pandas as pd

from bamboo._decorator import bamboo_transform
from bamboo._objects import BambooObject


@dataclass
class InRow(BambooObject):
    a: int
    b: int


@dataclass
class OutRow(BambooObject):
    a: int
    b: int


@bamboo_transform(InputType=InRow, OutputType=OutRow)
def inc_and_double_untyped(row):
    return OutRow(a=row.a + 1, b=row.b * 2)


def demo():
    df = pd.DataFrame({"a": [4, 5, 6], "b": [40, 50, 60]})
    print("input:\n", df)
    print("transformed:\n", df.apply(inc_and_double_untyped, axis=1))


if __name__ == "__main__":
    demo()
