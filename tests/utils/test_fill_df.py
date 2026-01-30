import unittest

import pandas as pd

from performance_tracker.utils.fill_df import fill_missing_dates, fill_unit


class FillDfTestCase(unittest.TestCase):
    def test_fill_missing_dates(self) -> None:
        dates = pd.to_datetime(["2026-01-01", "2026-01-03"])
        data = {"Close": [1.0, 3.0]}
        df_test = pd.DataFrame(data, index=dates)

        result = fill_missing_dates(df_test, val_col="Close")

        self.assertEqual(len(result), 3)
        self.assertEqual(result.index[1], pd.Timestamp("2026-01-02"))
        self.assertEqual(result.loc["2026-01-02", "Close"], 1.0)

        result_until = fill_missing_dates(df_test, val_col="Close", until="2026-01-05")

        self.assertEqual(len(result_until), 5)
        self.assertEqual(result_until.index[-1], pd.Timestamp("2026-01-05"))
        self.assertEqual(result_until.iloc[-1]["Close"], 3.0)

        result_today = fill_missing_dates(df_test, val_col="Close", until="today")
        expected_today = pd.Timestamp.now().normalize()

        self.assertEqual(result_today.index[-1], expected_today)

        with self.assertWarns(UserWarning):
            invalid_df = fill_missing_dates(df_test, val_col="Open")
            pd.testing.assert_frame_equal(invalid_df, df_test)

    def test_fill_unit(self) -> None:
        column_name = "Close"
        result = fill_unit(column_name)

        self.assertIn(column_name, result.columns)
        self.assertTrue((result[column_name] == 1.0).all())

        expected_start = pd.Timestamp("2015-01-01")
        self.assertEqual(result.index[0], expected_start)

        expected_end = pd.Timestamp.now().normalize()
        self.assertEqual(result.index[-1], expected_end)

        expected_days = (expected_end - expected_start).days + 1
        self.assertEqual(len(result), expected_days)

        self.assertIsInstance(result.index, pd.DatetimeIndex)
