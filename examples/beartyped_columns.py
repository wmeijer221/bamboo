"""Example: using bamboo with beartype runtime type-checking.

This example shows a typed Bamboo transformation decorated with
`@bamboo_transform` and also validated at runtime by `beartype`.
"""
from dataclasses import dataclass
import pandas as pd
import numpy as np

from beartype import beartype

from bamboo import BambooObject, bamboo_transform, validate


@beartype
@dataclass
class Row(BambooObject):
	a: int
	b: int


@beartype
@dataclass
class Out(Row):
	pass


@bamboo_transform
def add_and_mul(row: Row) -> Out:
	return Out(a=row.a + 1, b=row.b * 2)


def demo():
	df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
	validate(df, Row)
	print("input:\n", df)
	print("transformed:\n", df.apply(add_and_mul, axis=1))


if __name__ == "__main__":
	demo()
