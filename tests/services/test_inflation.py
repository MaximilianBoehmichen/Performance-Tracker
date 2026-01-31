import unittest
from unittest.mock import MagicMock, patch

import httpx
import pandas as pd

from performance_tracker.services.inflation import InflationService


class TestInflationService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = InflationService()
        self.mock_api_response = [
            {"page": 1, "pages": 1, "per_page": 100, "total": 2},
            [
                {"date": "2015", "value": 2.0, "country": {"id": "DE", "value": "Germany"}},
                {"date": "2016", "value": 1.5, "country": {"id": "DE", "value": "Germany"}}
            ]
        ]

    @patch("httpx.Client.get")
    def test_get_inflation_rate_success(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_api_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = self.service.get_inflation_rate("DEU")

        self.assertTrue(mock_get.called)

        self.assertIn("interpolated_inflation", df.columns)
        self.assertIsInstance(df.index, pd.DatetimeIndex)

        self.assertAlmostEqual(df.loc["2016-01-01", "interpolated_inflation"], 1.02)

    @patch("performance_tracker.services.inflation.fill_unit")
    def test_get_inflation_empty_country(self, mock_fill: MagicMock) -> None:
        mock_fill.return_value = pd.DataFrame()
        self.service.get_inflation_rate("")
        mock_fill.assert_called_once_with("interpolated_inflation")

    @patch("httpx.Client.get")
    def test_get_inflation_timeout(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = httpx.ReadTimeout("Timeout")

        with self.assertWarns(UserWarning), self.assertRaises(UnboundLocalError):
                self.service.get_inflation_rate("DEU")
