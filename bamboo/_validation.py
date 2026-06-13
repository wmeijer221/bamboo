from functools import lru_cache
from typing import Any, get_type_hints

import pandas as pd

from bamboo._exception import BambooException
from bamboo._objects import BambooType


def validate_input_output(InputType: BambooType, OutputType: BambooType, func, *args, **kwargs) -> pd.Series | pd.DataFrame:
    input_data = args[0]
    if isinstance(input_data, pd.Series):
        return _validate_input_output_series(InputType, OutputType, func, input_data, *args, **kwargs)
    elif isinstance(input_data, pd.DataFrame):
        return _validate_input_output_dataframe(InputType, OutputType, func, input_data, *args, **kwargs)
    raise BambooException(f"Expected input of type `pd.Series` or `pd.DataFrame`, received {type(input_data)}.")


def _validate_input_output_series(
    InputType: BambooType, OutputType: BambooType, func, input_series: pd.Series, *args, **kwargs
) -> pd.Series:
    # Gets the prototype (from cache) and sets the represented row.
    try:
        input_args = {
            str(key): value
            for key, value in input_series.to_dict().items()
        }
        transformation_input = InputType(**input_args)
    except Exception as ex:
        raise BambooException(f"Creating data object of type {InputType} with input {input_series} failed.") from ex

    # Do transformation
    transformation_args = (transformation_input, *args[1:])
    try:
        transformation_output = func(*transformation_args, **kwargs)
    except Exception as ex:
        raise BambooException("Data transformation raised an exception.") from ex

    # Parse output
    if not isinstance(transformation_output, OutputType):
        raise BambooException(f"Expected transformation of type {OutputType}, " f"but received {type(transformation_output)}")
    data: dict[str, Any] = vars(transformation_output)
    abandoned = _get_abandoned_columns(OutputType)
    data = {col: value for col, value in data.items() if col not in abandoned}
    transformation_output = pd.Series(data.values(), index=data.keys())

    return transformation_output


def _validate_input_output_dataframe(
    InputType: BambooType, OutputType: BambooType, func, input_data: pd.DataFrame, *args, **kwargs
) -> pd.DataFrame:
    def _parameterized_validate_input_output_series(input_series: pd.Series):
        return _validate_input_output_series(InputType, OutputType, func, input_series, *args, **kwargs)

    output_data = input_data.apply(_parameterized_validate_input_output_series, axis=1)
    return output_data


@lru_cache
def _get_abandoned_columns(BambooType: BambooType):
    empty_fields = set()
    for field_name, type_hint in get_type_hints(BambooType).items():
        if type_hint is type(None):
            empty_fields.add(field_name)
    return empty_fields
