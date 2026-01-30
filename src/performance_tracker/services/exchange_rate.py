import pandas as pd
from cachetools import TTLCache, cached

from performance_tracker.services.ticker import get_tickers
from performance_tracker.utils.fill_df import fill_missing_dates, fill_unit


class ExchangeRateService:
    @cached(cache=TTLCache(maxsize=128, ttl=60 * 60))
    def get_exchange_rate(self, from_symbol: str, to_symbol: str) -> pd.DataFrame:
        if from_symbol == to_symbol:
            return fill_unit("Close")

        ticker = get_tickers(f"{from_symbol}{to_symbol}=X")[0]
        history = ticker.history(period="10y")

        return fill_missing_dates(history, val_col="Close", until="today")

    def get_latest_exchange_rate(self, from_symbol: str, to_symbol: str) -> float:
        return self.get_exchange_rate(from_symbol, to_symbol)["Close"].iloc[-1]
