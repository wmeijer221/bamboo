"""Example: using bamboo transformations with tqdm and swifter.

This script demonstrates using `tqdm`'s `progress_apply` and `swifter`'s
`swifter.apply` to run Bamboo row transforms with progress/acceleration.
"""
from dataclasses import dataclass
import pandas as pd

from bamboo import BambooObject, bamboo_transform, validate


@dataclass
class Row(BambooObject):
    x: int


@dataclass
class Out(Row):
    pass


@bamboo_transform
def plus_one(r: Row) -> Out:
    return Out(x=r.x + 1)


def demo_tqdm():
    from tqdm import tqdm

    tqdm.pandas()
    df = pd.DataFrame({"x": range(20)})
    validate(df, Row)
    print("tqdm progress_apply input:\n", df.head())
    print("tqdm progress_apply result:\n", df.progress_apply(plus_one, axis=1).head())  # type: ignore


def demo_swifter():
    import swifter  # noqa: F401

    df = pd.DataFrame({"x": range(20)})
    validate(df, Row)
    print("\nswifter apply input:\n", df.head())
    print("swifter apply result:\n", df.swifter.apply(plus_one, axis=1).head())


def demo():
    demo_tqdm()
    demo_swifter()


if __name__ == "__main__":
    demo()
