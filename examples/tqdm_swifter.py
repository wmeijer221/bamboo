"""Example: using bamboo transformations with tqdm and swifter.

This script demonstrates using `tqdm`'s `progress_apply` and `swifter`'s
`swifter.apply` to run Bamboo row transforms with progress/acceleration.
"""
from dataclasses import dataclass
import pandas as pd

from bamboo._decorator import bamboo_transform
from bamboo._objects import BambooObject


@dataclass
class R(BambooObject):
    x: int


@dataclass
class Out(R):
    pass


@bamboo_transform
def plus_one(r: R) -> Out:
    return Out(x=r.x + 1)


def demo_tqdm():
    try:
        from tqdm import tqdm
    except Exception:  # pragma: no cover - optional dependency
        print("tqdm not installed; skipping tqdm demo")
        return

    tqdm.pandas()
    df = pd.DataFrame({"x": range(20)})
    print("tqdm progress_apply input:\n", df.head())
    print("tqdm progress_apply result:\n", df.progress_apply(plus_one, axis=1).head())


def demo_swifter():
    try:
        import swifter  # noqa: F401
    except Exception:  # pragma: no cover - optional dependency
        print("swifter not installed; skipping swifter demo")
        return

    df = pd.DataFrame({"x": range(20)})
    print("\nswifter apply input:\n", df.head())
    print("swifter apply result:\n", df.swifter.apply(plus_one, axis=1).head())


def demo():
    demo_tqdm()
    demo_swifter()


if __name__ == "__main__":
    demo()
