import pandas as pd

from bamboo._decorator import bamboo_transform, BambooType


def validate(df: pd.DataFrame, RowType: BambooType):
    @bamboo_transform(InputType=RowType, OutputType=RowType)
    def _identity(input):
        return input
    df.apply(_identity, axis=1)
