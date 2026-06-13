"""Example: vectorized operation with post-transformation validation.

This demonstrates the alternative pattern for large DataFrames: write your
transform as a normal vectorized pandas/swifter operation, then use `validate`
to sanity-check that the output conforms to your Bamboo row type.

This approach:
- Lets you use swifter/pandas' fast vectorized paths (no row-wise overhead).
- Still provides type-checking via validation.
- No @bamboo_transform decorator needed.
"""
from dataclasses import dataclass

import pandas as pd

from bamboo import BambooObject, validate


@dataclass
class InputRow(BambooObject):
    x: int
    y: int


@dataclass
class OutputRow(BambooObject):
    x: int
    y: int
    z: int


def demo():
    # Create input DataFrame
    df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
    print("input:\n", df)

    # Validate input conforms to InputRow
    validate(df, InputRow)
    print("input validation passed!")

    # Write transformation as normal vectorized pandas operation
    result = df.assign(z=df["x"] + df["y"])
    print("transformed:\n", result)

    # Validate output conforms to OutputRow
    validate(result, OutputRow)
    print("output validation passed!")


if __name__ == "__main__":
    demo()
