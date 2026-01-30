import pandas as pd
from yfinance import Ticker

from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService
from performance_tracker.utils.fill_df import fill_missing_dates


def join_all_df(
    comp_ticker_currency: str,
    comparison_ticker: Ticker,
    configdict: dict | None,
    currency: str,
    exchanger: ExchangeRateService,
    inflation_service: InflationService,
    ticker: Ticker,
    to_currency: str,
) -> pd.DataFrame:
    # basic raw information
    history_df = fill_missing_dates(
        ticker.history(period=configdict.get("period", "10y"), auto_adjust=True),
        val_col="Close",
        until="today",
    )

    comparison_history_df = fill_missing_dates(
        comparison_ticker.history(
            period=configdict.get("period", "10y"), auto_adjust=True
        ),
        val_col="Close",
        until="today",
    )

    exchange_rates_df = exchanger.get_exchange_rate(currency, to_currency)
    exchange_rates_comp_df = exchanger.get_exchange_rate(
        comp_ticker_currency, to_currency
    )
    inflation_df = inflation_service.get_inflation_rate(configdict.get("country", ""))

    # remove timezones
    history_df.index = pd.DatetimeIndex(history_df.index).tz_localize(None)
    comparison_history_df.index = pd.DatetimeIndex(
        comparison_history_df.index
    ).tz_localize(None)
    exchange_rates_df.index = pd.DatetimeIndex(exchange_rates_df.index).tz_localize(
        None
    )
    exchange_rates_comp_df.index = pd.DatetimeIndex(
        exchange_rates_comp_df.index
    ).tz_localize(None)
    inflation_df.index = pd.DatetimeIndex(inflation_df.index).tz_localize(None)

    # graph calculation
    history_currency_df = history_df.join(
        exchange_rates_df[["Close"]], how="left", rsuffix="_Exchange"
    )
    history_currency_df = history_currency_df.join(
        exchange_rates_comp_df[["Close"]],
        how="left",
        rsuffix="_Comparison_Exchange",
    )
    history_currency_df = history_currency_df.join(
        comparison_history_df[["Close"]], how="left", rsuffix="_Comparison"
    )
    history_currency_df["Close_Exchange"].ffill()
    history_currency_df["Close_Adjusted"] = (
        history_currency_df["Close"] * history_currency_df["Close_Exchange"]
    )
    history_currency_df["Close_Adjusted"] = (
        history_currency_df["Close_Adjusted"]
        * 100
        / history_currency_df["Close_Adjusted"].iloc[0]
    )

    history_currency_df["Close_Comparison_Adjusted"] = (
        history_currency_df["Close_Comparison"]
        * history_currency_df["Close_Comparison_Exchange"]
    )

    starting_date = history_currency_df.index[0].replace(tzinfo=None)
    starting_inflation = inflation_df["interpolated_inflation"].asof(starting_date)

    inflation_df["interpolated_inflation_adjusted"] = (
        inflation_df["interpolated_inflation"] * 100 / starting_inflation
    )
    combined_df = history_currency_df.join(
        inflation_df[["interpolated_inflation_adjusted"]], how="left"
    )
    combined_df["Close_Comparison_Adjusted"] = (
        combined_df["Close_Comparison_Adjusted"]
        * 100
        / combined_df["Close_Comparison_Adjusted"].iloc[0]
    )

    return combined_df
