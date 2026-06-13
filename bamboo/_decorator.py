import inspect
from typing import Optional, Callable, Any, get_type_hints, overload, Union

import pandas as pd


from bamboo._exception import BambooException
from bamboo._objects import BambooObject, BambooType
from bamboo._validation import validate_input_output


@overload
def bamboo_transform(func: Callable[..., Any]) -> Callable[[pd.Series], pd.Series]: ...


@overload
def bamboo_transform(
    *, InputType: BambooType, OutputType: BambooType
) -> Callable[[Callable[..., Any]], Callable[[pd.Series], pd.Series]]: ...


def bamboo_transform(
    func: Optional[Callable[..., Any]] = None,
    *,
    InputType: Optional[BambooType] = None,
    OutputType: Optional[BambooType] = None,
) -> Union[Callable[[pd.Series], pd.Series], Callable[[Callable[..., Any]], Callable[[pd.Series], pd.Series]]]:
    """Wrap a row transformation with Bamboo input/output validation.

    This decorator allows a function that accepts and returns subclasses of
    :class:`bamboo._objects.BambooObject` to be used as a row-wise function
    for ``pandas.DataFrame.apply(..., axis=1)``. The decorator converts each
    ``pd.Series`` row into the declared input type and converts the output
    object back into a ``pd.Series``.

    The decorator can be used in two forms:

    - ``@bamboo_transform`` when the function signature already contains
      explicit type hints for both the first argument and the return value.
    - ``@bamboo_transform(InputType=..., OutputType=...)`` when you want to
      specify the input and output Bamboo types explicitly.

    Parameters
    ----------
    func:
        The function being decorated. If ``None``, returns a decorator factory
        accepting ``InputType`` and ``OutputType``.
    InputType:
        A Bamboo subclass type to construct from each input ``pd.Series``.
    OutputType:
        A Bamboo subclass type expected from the decorated function.

    Returns
    -------
    callable:
        Either the wrapped row transformer or a decorator factory.
    """

    if func is not None:
        return _create_inferred_wrapper(func)
    elif InputType is not None and OutputType is not None:
        return _create_parameterized_wrapper(InputType, OutputType)

    raise ValueError(
        "`InputType` and `OutputType` must be specified",
        "when `func` is not specified. If you do not",
        "want to manually specify input and output",
        "types, you should use `@bamboo_transform` instead",
        "of `@bamboo_transform()`.",
    )


def _create_inferred_wrapper(func: Callable[..., Any]) -> Callable[[pd.Series], pd.Series]:
    func_signature = inspect.signature(func)
    param_names = list(func_signature.parameters.keys())

    if param_names is None:
        raise BambooException(f"Function {func.__name__} must have at least one input argument.")
    first_param = param_names[0]

    type_hints = get_type_hints(func)
    InputType = type_hints.get(first_param)
    OutputType = type_hints.get("return")

    if (
        InputType is None
        or OutputType is None
        or not issubclass(InputType, BambooObject)
        or not issubclass(OutputType, BambooObject)
    ):
        raise BambooException(
            f"Function `{func.__name__}` must have explicit type hints "
            "for both its first argument and its return value. These"
            "types must inherit `BaseType`."
        )

    def _parameterized_verify_input_output(*args, **kwargs):
        result = validate_input_output(InputType, OutputType, func, *args, **kwargs)
        return result

    return _parameterized_verify_input_output


def _create_parameterized_wrapper(
    InputType: BambooType, OutputType: BambooType
) -> Callable[[Callable[..., Any]], Callable[[pd.Series], pd.Series]]:
    def _pd_transform_wrapper(func: Callable[..., Any]) -> Callable[[pd.Series], pd.Series]:
        def _manually_parameterized_verify_input_output(*args, **kwargs) -> pd.Series:
            result = validate_input_output(InputType, OutputType, func, *args, **kwargs)
            return result

        return _manually_parameterized_verify_input_output

    return _pd_transform_wrapper
