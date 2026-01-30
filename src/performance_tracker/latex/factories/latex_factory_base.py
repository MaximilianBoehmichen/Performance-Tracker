from abc import ABC, abstractmethod

import pandas as pd
from yfinance import Ticker

from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService


class LaTeXFactoryBase(ABC):
    """Base Factory to generate LaTeX code."""

    @abstractmethod
    def generate(
        self,
        ticker_info: dict,
        combined_df: pd.DataFrame,
        ticker: Ticker,
        comparison_ticker: Ticker,
        inflation_service: InflationService,
        exchanger: ExchangeRateService,
        configdict: dict | None = None,
    ) -> str:
        """Generates the LaTeX code.
        :param ticker_info:
        :param combined_df:
        :param inflation_service:
        :param comparison_ticker:
        :param ticker: yfinance ticker of isin
        :param exchanger:
        :param configdict: configdict of input
        """
        pass

    def __call__(self, **kwargs) -> str:
        return self.generate(**kwargs)
