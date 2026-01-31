import unittest
from unittest.mock import MagicMock

from performance_tracker.latex.factories.price_target_factory import PriceTargetFactory


class TestPriceTargetFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = PriceTargetFactory()

        self.mock_ticker = MagicMock()
        self.mock_ticker.info = {"currency": "USD", "previousClose": 150.0}
        self.mock_ticker.analyst_price_targets = {
            "high": 200.0,
            "low": 100.0,
            "mean": 160.0,
            "median": 155.0
        }

        self.mock_df = MagicMock()
        self.mock_inf = MagicMock()
        self.mock_exc = MagicMock()

    def test_generate_standard_case(self) -> None:
        result = self.factory.generate(
            ticker_info={},
            combined_df=self.mock_df,
            ticker=self.mock_ticker,
            comparison_ticker=self.mock_ticker,
            inflation_service=self.mock_inf,
            exchanger=self.mock_exc
        )

        self.assertIn(r"\begin{tikzpicture}", result)
        self.assertIn("Currently: 150.00", result)
        self.assertIn("Min: 100.00", result)
        self.assertIn("Max: 200.00", result)

        self.assertIn("Mean Analyst Price Target", result)

    def test_zero_width_logic(self) -> None:
        self.mock_ticker.info["previousClose"] = 100.0
        self.mock_ticker.analyst_price_targets = {"high": 100.0, "low": 100.0}

        result = self.factory.generate(
            ticker_info={},
            combined_df=self.mock_df,
            ticker=self.mock_ticker,
            comparison_ticker=self.mock_ticker,
            inflation_service=self.mock_inf,
            exchanger=self.mock_exc
        )

        self.assertIn("x=\\textwidth/1", result)

    def test_missing_analyst_data(self) -> None:
        self.mock_ticker.analyst_price_targets = {"high": 200, "low": 100}

        result = self.factory.generate(
            ticker_info={},
            combined_df=self.mock_df,
            ticker=self.mock_ticker,
            comparison_ticker=self.mock_ticker,
            inflation_service=self.mock_inf,
            exchanger=self.mock_exc
        )

        self.assertNotIn("Mean Analyst Price Target", result)
