# Bamboo

Current version: "0.0.2"

Bamboo is a small library that adds structure and validation to pandas
DataFrame row-transformations. It provides a lightweight way to declare the
expected input and output shapes for a row-wise transformation using simple
Bamboo data objects, and a decorator that converts between `pd.Series` rows
and your typed objects while validating inputs and outputs.

Why use bamboo
- **Safer transforms:** validate that each row can be converted into the
  declared input type and the transformation returns the expected output
  type.
- **Documented data contracts:** row types live next to your transform code,
  making the expected inputs/outputs explicit and easy to read.
- **Plays nicely with tooling:** works with `tqdm`, `swifter`, and runtime
  type checkers like `beartype` (see examples).

## Quick example

This example demonstrates the default, type-hinted usage with `@bamboo_transform`.

```python
from dataclasses import dataclass
import pandas as pd

from bamboo import BambooObject, bamboo_transform


@dataclass
class Row(BambooObject):
    a: int
    b: int


@dataclass
class Out(Row):
    pass


@bamboo_transform
def add_and_mul(row: Row) -> Out:
    return Out(a=row.a + 1, b=row.b * 2)


df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
validate(df, Row)
print(df.apply(add_and_mul, axis=1))
```

## More examples

See the `examples` folder for:
- `default_typed.py` — inferred typed example (default use-case).
- `default_untyped.py` — parameterized decorator for un-annotated functions.
- `vectorized_validate.py` — write fast vectorized operations, then validate output with `validate()`.
- `tqdm_swifter.py` — shows compatibility with `tqdm` and `swifter`.
- `beartyped_columns.py` — example using `beartype` for runtime type checking.

## Patterns

**Row-wise with @bamboo_transform:** Use when you need per-row type validation as
you transform. Good for smaller datasets or when type contracts are critical.
Works with `tqdm`, but may be slower with `swifter` (only row-wise path).

**Vectorized + validate:** Write fast vectorized operations (using pandas,
`swifter`, or NumPy) and call `validate()` on the result as a sanity check.
Good for large datasets where raw speed matters; validation happens after
the fast operation completes.

## Running examples

Install dev dependencies:

```bash
poetry install
```

Run an individual example:

```bash
python examples/default_typed.py
python examples/vectorized_validate.py
python examples/tqdm_swifter.py
python examples/beartyped_columns.py
```

## Development

Install dev dependencies:

```bash
poetry install
```

See the Makefile for common commands.

## License

MIT
