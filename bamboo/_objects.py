from typing import get_type_hints, TypeAlias, Type


class BambooObject:
    """Base class for Bamboo row models.

    Subclass :class:`BambooObject` to declare the typed fields that represent a
    single DataFrame row for use with :func:`bamboo.bamboo_transform`.

    Users typically define a dataclass subclass of :class:`BambooObject` and
    then annotate transformation functions against that subclass. Bamboo
    handles constructing the object from a row and converting the returned
    object back into a ``pd.Series``.
    """


BambooType: TypeAlias = Type[BambooObject]
