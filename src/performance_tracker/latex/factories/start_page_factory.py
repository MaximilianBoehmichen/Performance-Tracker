import pandas as pd
from yfinance import Ticker

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService


class StartPageFactory(LaTeXFactoryBase):
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
        return r"""
        \documentclass{perftracker}
        \begin{document}
        """
