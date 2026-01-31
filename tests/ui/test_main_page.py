import unittest
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

import performance_tracker.ui.main_page as app


class MockSessionState(dict):
    def __getattr__(self, key: object) -> object:
        return self[key]

    def __setattr__(self, key: object, value: object) -> None:
        self[key] = value


class TestStreamlitApp(unittest.TestCase):
    def setUp(self) -> None:
        self.state = MockSessionState()

        self.state.df = pd.DataFrame(columns=[
            "Ticker", "Quantity", "Purchase Date",
            "Purchase Price", "Sell Date", "Sell Price"
        ])
        self.state.shared_data = {}
        self.state.input_df = pd.DataFrame()
        self.state.csv_uploader = None

    def test_handle_upload_success(self) -> None:
        with patch("streamlit.session_state", new=self.state), \
                patch("streamlit.error") as mock_st_error, \
                patch("pandas.read_csv") as mock_read:
            mock_file = MagicMock()
            mock_file.file_id = "123"
            self.state.csv_uploader = mock_file

            mock_read.return_value = pd.DataFrame({
                "Ticker": ["AAPL"], "Quantity": [10],
                "Purchase Date": ["2023-01-01"], "Purchase Price": [150.0],
                "Sell Date": ["2023-02-01"], "Sell Price": [160.0]
            })

            app.handle_upload()

            self.assertEqual(self.state.uploaded_file_id, "123")
            self.assertEqual(self.state.df.iloc[0]["Ticker"], "AAPL")
            mock_st_error.assert_not_called()

    def test_start_analysis_logic(self) -> None:
        local_state = MockSessionState()
        local_state.shared_data = {"is_running": False}
        local_state.is_running = False

        local_state.input_df = pd.DataFrame({
            "Ticker": ["AAPL"],
            "Quantity": [1],
            "Purchase Date": [date(2023, 1, 1)],
            "Purchase Price": [150.0],
            "Sell Date": [pd.NaT],
            "Sell Price": [0.0]
        })

        with patch("performance_tracker.ui.main_page.Worker") as mock_worker, \
                patch("streamlit.session_state", new=local_state):
            mock_worker.return_value = MagicMock()

            app.start_analysis("Euro", "Germany", "10 years")

            mock_worker.assert_called_once()

            args = mock_worker.call_args[0]
            config = args[1]
            self.assertEqual(config["period"], "10y")
            self.assertEqual(config["currency"], "EUR")
