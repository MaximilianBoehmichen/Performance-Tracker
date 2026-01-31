import unittest
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

from performance_tracker.latex.factories.chart_graph_factory import ChartGraphFactory


class TestChartGraphFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = ChartGraphFactory()

        dates = pd.date_range(start="2023-01-01", periods=5, freq="D")
        self.mock_df = pd.DataFrame({
            "Close_Adjusted": [100.0, 105.0, 110.0, 108.0, 115.0],
            "interpolated_inflation_adjusted": [100.0, 100.1, 100.2, 100.3, 100.4],
            "Close_Comparison_Adjusted": [100.0, 102.0, 104.0, 106.0, 108.0]
        }, index=dates)

        self.mock_ticker = MagicMock()
        self.mock_ticker.info = {"previousClose": 150.0, "currency": "USD", "symbol": "AAPL"}
        self.mock_ticker.dividends = pd.Series([], dtype=float)

        self.mock_comp_ticker = MagicMock()
        self.mock_comp_ticker.info = {"symbol": "PAS.ED"}

        self.mock_inf = MagicMock()
        self.mock_exc = MagicMock()

    def test_generate_contains_key_latex_elements(self) -> None:
        config = {"period": "1y"}
        result = self.factory.generate(
            {}, self.mock_df, self.mock_ticker,
            self.mock_comp_ticker, self.mock_inf, self.mock_exc, config
        )

        self.assertIn(r"\begin{tikzpicture}", result)
        self.assertIn(r"date ZERO=2023-01-01", result)
        self.assertIn("150.00", result)
        self.assertIn("PAS.ED", result)

    def test_get_percent_performance_positive(self) -> None:
        perf_str = self.factory.get_percent_performance(self.mock_df, "Close_Adjusted")
        self.assertIn("+15.00", perf_str)
        self.assertIn("green!70!black", perf_str)

    def test_get_percent_performance_negative(self) -> None:
        dates = pd.date_range(start="2023-01-01", periods=2, freq="D")
        negative_df = pd.DataFrame({
            "Close_Adjusted": [100.0, 90.0]
        }, index=dates)

        perf_str = self.factory.get_percent_performance(negative_df, "Close_Adjusted")

        self.assertIn("-10.00", perf_str)
        self.assertIn("red!70!black", perf_str)
        self.assertNotIn("+", perf_str)

    def test_get_xticks_5y(self) -> None:
        start = datetime(2018, 1, 1)
        end = datetime(2023, 1, 1)
        ticks, labels = self.factory.get_xticks(start, end, "5y")

        expected_ticks = "2023-01-01, 2022-01-01, 2021-01-01, 2020-01-01, 2019-01-01"
        expected_labels = "Jan 2023, Jan 2022, Jan 2021, Jan 2020, Jan 2019"

        self.assertEqual(ticks, expected_ticks)
        self.assertEqual(labels, expected_labels)

    def test_get_xticks_10y(self) -> None:
        start = datetime(2013, 1, 1)
        end = datetime(2023, 1, 1)
        ticks, labels = self.factory.get_xticks(start, end, "10y")

        expected_ticks = ("2023-01-01, 2022-01-01, 2021-01-01, 2020-01-01, 2019-01-01, "
                          "2018-01-01, 2017-01-01, 2016-01-01, 2015-01-01, 2014-01-01")
        expected_labels = "Jan 2023, , Jan 2021, , Jan 2019, , Jan 2017, , Jan 2015, "

        self.assertEqual(ticks, expected_ticks)
        self.assertEqual(labels, expected_labels)

    def test_get_datapoints_format(self) -> None:
        points = self.factory.get_datapoints(self.mock_df, "Close_Adjusted")
        self.assertIn("(2023-01-01, 100.0)", points)


class TestChartGraphFactoryExtraTicks(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = ChartGraphFactory()

    def test_get_extra_xticks_success(self) -> None:
        start_date = datetime(2023, 1, 1)
        idx = pd.to_datetime(["2023-01-05", "2023-01-10"]).tz_localize("UTC")
        dividends = pd.Series([0.5, 0.5], index=idx)

        result = self.factory.get_extra_xticks(dividends, start_date)

        self.assertIn("extra x ticks={ 2023-01-05, 2023-01-10 }", result)
        self.assertIn("extra x tick labels={ , }", result)

    def test_get_extra_xticks_filtering(self) -> None:
        start_date = datetime(2023, 1, 1)
        idx = pd.to_datetime(["2022-12-31", "2023-01-05"]).tz_localize("UTC")
        dividends = pd.Series([0.5, 0.5], index=idx)

        result = self.factory.get_extra_xticks(dividends, start_date)

        self.assertIn("extra x ticks={ 2023-01-05 }", result)
        self.assertNotIn("2022-12-31", result)
        self.assertIn("extra x tick labels={  }", result)

    def test_get_extra_xticks_empty_cases(self) -> None:
        start_date = datetime(2023, 1, 1)

        self.assertEqual(self.factory.get_extra_xticks(pd.Series([]), start_date), "")

        wrong_idx_series = pd.Series([1], index=["NotADate"])
        self.assertEqual(self.factory.get_extra_xticks(wrong_idx_series, start_date), "")
