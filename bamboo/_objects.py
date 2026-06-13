from typing import get_type_hints, TypeAlias, Type

import pandas as pd


class BambooObject:
    def __init__(self):
        self._type_hints: set[str] = set(get_type_hints(type(self)).keys())

    def _set_represented_row(self, represented_row: pd.Series):
        """
        Proxy method to use a single prototype object that can
        represent all rows in a dataframe. Any access to the
        attributes is intercepted.
        """
        self._represented_row = represented_row

    def __getattribute__(self, name: str):
        state = super().__getattribute__("__dict__")
        # General defer
        if name.startswith("_") or name not in state:
            return super().__getattribute__(name)
        # Defer if not dealing with a prototype.
        if "_represented_row" not in state:
            return super().__getattribute__(name)
        # Get from represented row.
        repr_row = state["_represented_row"]
        value = repr_row[name]
        return value


BambooType: TypeAlias = Type[BambooObject]
