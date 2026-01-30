import warnings
from functools import lru_cache

import httpx
import pandas as pd
import yfinance as yf
from yfinance import Ticker


def get_tickers(names: str | list[str]) -> list[Ticker]:
    if isinstance(names, str):
        names = [names]

    if not isinstance(names, list):
        raise TypeError("name must be a list")

    try:
        tickers = [_get_ticker(name) for name in names]
    except httpx.ReadTimeout:
        warnings.warn(f"ReadTimeout for tickers {names}", stacklevel=2)
        return []

    return tickers


@lru_cache(maxsize=100)
def _get_ticker(name: str) -> Ticker | None:
    try:
        return yf.Ticker(ticker=name)
    except Exception:
        warnings.warn(f"Couldn't fetch ticker {name}", stacklevel=2)
        return None


if __name__ == "__main__":
    import json

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 350)
    t = get_tickers(names="SAP.DE")
    print(json.dumps(t[0].info, indent=4))
    print(t[0].recommendations)
    print(t[0].dividends)
    print(t[0].growth_estimates)
    print(t[0].news)
    print(t[0].major_holders)
    print(t[0].cashflow)
    print(t[0].balance_sheet)
    print(t[0].financials)
    print(t[0].actions)
    print(t[0].analyst_price_targets)
    print(t[0].funds_data)
    print(t[0].incomestmt)
    print(t[0].recommendations_summary)
    print(t[0].sec_filings)
    print(t[0].sustainability)
    print(t[0].options)
