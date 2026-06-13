import pandas as pd

from bamboo._decorator import bamboo_transform, BambooType


def validate(df: pd.DataFrame, RowType: BambooType):
    """Validate that a DataFrame conforms to a Bamboo row type.

    This helper applies a no-op Bamboo transformation over each row of the
    DataFrame and raises a ``BambooException`` if any row cannot be converted
    into the declared Bamboo type.

    Parameters
    ----------
    df:
        The DataFrame to validate.
    RowType:
        The Bamboo row type that each row should conform to.
    """

    @bamboo_transform(InputType=RowType, OutputType=RowType)
    def _identity(input):
        return input

    df.apply(_identity, axis=1)
