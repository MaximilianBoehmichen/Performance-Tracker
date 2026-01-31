import unittest
from unittest.mock import MagicMock

import pandas as pd

from performance_tracker.latex.factories.data_and_recommendations import (
    DataAndRecommendationsFactory,
)


class TestDataAndRecommendationsFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = DataAndRecommendationsFactory()

        self.mock_df = pd.DataFrame({
            "Close_Adjusted": [110, 120, 105, 130],
            "Close_Comparison_Adjusted": [100, 115, 110, 120],
            "interpolated_inflation_adjusted": [100, 100, 100, 100]
        })

        self.mock_ticker = MagicMock()

        self.mock_ticker.recommendations = pd.DataFrame([{
            "strongBuy": 5, "buy": 10, "hold": 2, "sell": 1, "strongSell": 0
        }])

        self.mock_ticker.no_recommendations = pd.DataFrame([{
            "strongBuy": 0, "buy": 0, "hold": 0, "sell": 0, "strongSell": 0
        }])

        self.mock_ticker.cashflow = pd.DataFrame(
            {"2023-12-31": [5000000]},
            index=["Free Cash Flow"]
        )

        self.mock_ticker.growth_estimates = pd.DataFrame(
            {"stockTrend": [0.15]},
            index=["+1y"]
        )

        self.mock_ticker.info = {
            "operatingCashflow": 6000000,
            "enterpriseValue": 100000000,
            "fullTimeEmployees": 500,
            "overallRisk": 3,
            "fiveYearAvgDividendYield": 2.5,
            "beta": 1.1234
        }

    def test_get_percentage_larger_logic(self) -> None:
        result = self.factory.get_percentage_larger(
            self.mock_df, "Close_Adjusted", "Close_Comparison_Adjusted"
        )

        self.assertIn(r"75.0\%", result)
        self.assertIn("mainColour", result)

    def test_get_percentage_larger_red_color(self) -> None:
        low_perf_df = pd.DataFrame({
            "A": [90, 80],
            "B": [100, 100]
        })
        result = self.factory.get_percentage_larger(low_perf_df, "A", "B")
        self.assertIn(r"0.0\%", result)
        self.assertIn("red", result)

    def test_get_recommendations_bar_graph_empty(self) -> None:
        empty_df = pd.DataFrame()
        result = self.factory.get_recommendations_bar_graph(empty_df)
        self.assertEqual(result, "No recommendations available")

        result = self.factory.get_recommendations_bar_graph(self.mock_ticker.no_recommendations)
        self.assertEqual(result, "No recommendations available")

    def test_get_recommendations_math(self) -> None:
        result = self.factory.get_recommendations_bar_graph(self.mock_ticker.recommendations)

        self.assertIn("Recommendations (18)", result)
        self.assertNotIn("Hold (2)", result)

    def test_get_data_table_formatting(self) -> None:
        result = self.factory.get_data_table(self.mock_ticker, self.mock_df, "USD")

        self.assertIn("1.123", result)
        self.assertIn(r"15.0\%", result)
        self.assertIn(r"\textbf{ 75.0\% }", result)

    def test_generate_integration_structure(self) -> None:
        mock_comparison = MagicMock()
        mock_comparison.info = {"symbol": "SPY"}

        result = self.factory.generate(
            ticker_info={},
            combined_df=self.mock_df,
            ticker=self.mock_ticker,
            comparison_ticker=mock_comparison,
            inflation_service=MagicMock(),
            exchanger=MagicMock(),
            configdict={"currency": "USD"}
        )

        self.assertIn(r"\begin{minipage}{0.48\textwidth}", result)
        self.assertIn(r"\hfill", result)

        self.assertIn("Growth Estimate:", result)
        self.assertIn(r"15.0\%", result)
        self.assertIn("1.123", result)

        self.assertIn("Recommendations (18)", result)
        self.assertIn(r"\begin{tikzpicture}", result)

    def test_generate_with_empty_recommendations(self) -> None:
        self.mock_ticker.recommendations = pd.DataFrame()

        result = self.factory.generate(
            ticker_info={},
            combined_df=self.mock_df,
            ticker=self.mock_ticker,
            comparison_ticker=MagicMock(),
            inflation_service=MagicMock(),
            exchanger=MagicMock(),
            configdict={"currency": "EUR"}
        )

        self.assertIn("No recommendations available", result)
