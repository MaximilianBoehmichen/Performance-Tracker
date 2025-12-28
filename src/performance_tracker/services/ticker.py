import warnings
from typing import List, Union

import pandas as pd
import yfinance as yf
from yfinance import Ticker

from performance_tracker.utils import isin_validation


def get_tickers(names: Union[str, List[str]]) -> List[Ticker]:
    if isinstance(names, str):
        names = [names]

    if not isinstance(names, list):
        raise TypeError("name must be a list")

    validated_isins = isin_validation.validate(names)
    invalid_isins = [k for k, v in validated_isins.items() if not v]
    warnings.warn(
        f"Invalid ISINs: {invalid_isins}", stacklevel=2
    ) if invalid_isins else None
    filtered_isins = {k: v for k, v in validated_isins.items() if v}

    return [yf.Ticker(ticker=isin) for isin in filtered_isins]


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    t = get_tickers(names="DE000BAY0017")
    print(t[0].info)
