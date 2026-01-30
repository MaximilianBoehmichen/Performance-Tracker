import unittest

from performance_tracker.utils.short_number_rep import short_rep


class TestShortRep(unittest.TestCase):
    def test_basic_numbers(self) -> None:
        (self.assertEqual(short_rep(500), "500"),)
        self.assertEqual(short_rep(0), "0.00")
        self.assertEqual(short_rep(None), "")

    def test_negative_numbers(self) -> None:
        self.assertEqual(short_rep(-500), "-500")
        self.assertEqual(short_rep(-1500), "-1.50k")
        self.assertEqual(short_rep(-1_500_000_000), "-1.50B")

    def test_strings_and_types(self) -> None:
        self.assertEqual(short_rep("1000"), "1.00k")
        self.assertEqual(short_rep("hello"), "")

    def test_thousands(self) -> None:
        self.assertEqual(short_rep(1100), "1.10k")
        self.assertEqual(short_rep(11000), "11.0k")
        self.assertEqual(short_rep(110000), "110k")

    def test_millions(self) -> None:
        self.assertEqual(short_rep(1_200_000), "1.20M")
        self.assertEqual(short_rep(12_000_000), "12.0M")
        self.assertEqual(short_rep(120_000_000), "120M")

    def test_billions(self) -> None:
        self.assertEqual(short_rep(5_020_000_000), "5.02B")
        self.assertEqual(short_rep(12_300_000_000), "12.3B")
        self.assertEqual(short_rep(999_000_000_000), "999B")

    def test_trillions(self) -> None:
        self.assertEqual(short_rep(4_000_000_000_000), "4.00T")
        self.assertEqual(short_rep(40_000_000_000_000), "40.0T")

    def test_infinity(self) -> None:
        self.assertEqual(short_rep(-float("inf")), "-INF")
