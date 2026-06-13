from functools import lru_cache
from typing import Any, get_type_hints
import threading

import pandas as pd

from bamboo._exception import BambooException
from bamboo._objects import BambooObject, BambooType


_thread_local = threading.local()


def validate_input_output(InputType: BambooType, OutputType: BambooType, func, *args, **kwargs) -> pd.Series:
    # Get and parse input
    input_series = args[0]

    if not isinstance(input_series, pd.Series):
        raise BambooException(f"Excepted input of type `pd.Series`, received {type(input_series)}.")

    # Gets the prototype (from cache) and sets the represented row.
    try:
        transformation_input = _get_prototype(InputType, input_series)
    except Exception as ex:
        raise BambooException(f"Creating data object prototype of type {InputType} failed.") from ex

    transformation_input._set_represented_row(input_series)

    # Do transformation
    transformation_args = (transformation_input, *args[1:])
    try:
        transformation_output = func(*transformation_args, **kwargs)
    except Exception as ex:
        raise BambooException("Data transformation raised an exception.") from ex

    # Parse output
    if not isinstance(transformation_output, OutputType):
        raise BambooException(f"Excpected transformation of type {OutputType}, " f"but received {type(transformation_output)}")
    data: dict[str, Any] = vars(transformation_output)
    abandoned = _get_abandoned_columns(OutputType)
    data = {col: value for col, value in data.items() if col not in abandoned}
    transformation_output = pd.Series(data.values(), index=data.keys())

    return transformation_output


@lru_cache
def _get_abandoned_columns(BambooType: BambooType):
    empty_fields = set()
    for field_name, type_hint in get_type_hints(BambooType).items():
        if type_hint is type(None):
            empty_fields.add(field_name)
    return empty_fields


def _get_prototype(BambooType: BambooType, input_series: pd.Series) -> BambooObject:
    cache = getattr(_thread_local, "prototype_cache", None)
    if cache is None:
        cache = dict()
        _thread_local.prototype_cache = cache

    prototype = cache.get(BambooType)
    if prototype is None:
        prototype = BambooType(**input_series)
        cache[BambooType] = prototype

    return prototype
