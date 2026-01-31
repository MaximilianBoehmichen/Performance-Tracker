import unittest

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase


class TestLaTeXFactoryBase(unittest.TestCase):

    def test_cannot_instantiate_abstract_class(self) -> None:
        with self.assertRaises(TypeError):
            LaTeXFactoryBase()

    def test_call_magic_method_forwards_to_generate(self) -> None:
        class DummyFactory(LaTeXFactoryBase):
            def generate(self, **kwargs) -> str:
                return "success"

        factory = DummyFactory()

        result = factory(ticker_info={}, combined_df=None, ticker=None,
                         comparison_ticker=None, inflation_service=None,
                         exchanger=None)

        self.assertEqual(result, "success")

    def test_generate_enforcement(self) -> None:
        class IncompleteFactory(LaTeXFactoryBase):
            pass

        with self.assertRaises(TypeError):
            IncompleteFactory()
