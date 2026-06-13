from typing import get_type_hints, TypeAlias, Type, Optional

import pandas as pd


class BambooObject:
    """Base class for Bamboo row models.

    Subclass :class:`BambooObject` to declare the typed fields that represent a
    single DataFrame row for use with :func:`bamboo.bamboo_transform`.

    Users typically define a dataclass subclass of :class:`BambooObject` and
    then annotate transformation functions against that subclass. Bamboo
    handles constructing the object from a row and converting the returned
    object back into a ``pd.Series``.
    """

    def __init__(self):
        self._type_hints: set[str] = set(get_type_hints(type(self)).keys())

    def _set_represented_row(self, represented_row: Optional[pd.Series]):
        """Bind the current row to this Bamboo object.

        This is an internal helper used by Bamboo during row-wise validation and
        transformation. It should not be called directly by user code.

        Parameters
        ----------
        represented_row:
            The ``pd.Series`` object representing the current DataFrame row.
        """
        self._represented_row = represented_row

    def __getattribute__(self, name: str):
        state = super().__getattribute__("__dict__")
        # General defer
        if name.startswith("_") or name not in state:
            return super().__getattribute__(name)
        # Defer if not dealing with a prototype.
        if "_represented_row" not in state or state["_represented_row"] is None:
            return super().__getattribute__(name)
        # Get from represented row.
        repr_row = state["_represented_row"]
        value = repr_row[name]
        return value


BambooType: TypeAlias = Type[BambooObject]
