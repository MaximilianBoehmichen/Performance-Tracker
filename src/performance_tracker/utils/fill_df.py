import warnings
from datetime import datetime

import pandas as pd


def fill_missing_dates(
    df: pd.DataFrame, val_col: str, until: str = None
) -> pd.DataFrame:
    if not ({val_col}.issubset(df.columns) and isinstance(df.index, pd.DatetimeIndex)):
        warnings.warn("supplied df does not meet the requirements", stacklevel=2)
        return df

    df.index = df.index.tz_localize(None)

    if until:
        if until == "today":
            until = pd.Timestamp.now().strftime("%Y-%m-%d")

        daily_df = pd.DataFrame(
            index=pd.date_range(
                start=df.index[0].replace(tzinfo=None), end=until, tz=None, freq="D"
            )
        )
        df = daily_df.join(df[val_col], how="left")

    df_filled = df.asfreq("D")
    df_filled[val_col] = df_filled[val_col].ffill()

    return df_filled


def fill_unit(val_col: str) -> pd.DataFrame:
    end_date = datetime.now()
    start_date = datetime(2015, 1, 1)

    daily_df = pd.DataFrame(
        index=pd.date_range(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            tz=None,
            freq="D",
        )
    )
    daily_df[val_col] = 1.0

    return daily_df
