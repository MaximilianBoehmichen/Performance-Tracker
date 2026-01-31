import unittest
from unittest.mock import MagicMock

import pandas as pd
from parameterized import parameterized

from performance_tracker.latex.factories.end_page_factory import EndPageFactory
from performance_tracker.latex.factories.full_width_rule_factory import (
    FullWidthRuleFactory,
)
from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.latex.factories.new_page_factory import NewPageFactory
from performance_tracker.latex.factories.start_page_factory import StartPageFactory


class TestStaticFactories(unittest.TestCase):
    def setUp(self) -> None:
        self.args = {
            "ticker_info": {},
            "combined_df": pd.DataFrame(),
            "ticker": MagicMock(),
            "comparison_ticker": MagicMock(),
            "inflation_service": MagicMock(),
            "exchanger": MagicMock(),
            "configdict": None
        }

    @parameterized.expand([
        (EndPageFactory(), r"\end{document}"),
        (FullWidthRuleFactory(), r"\noindent{\color{black}\rule{\textwidth}{1pt}}\par"),
        (NewPageFactory(), r"""
        \zlabel{LastPage}
        \newpage
        """),
        (StartPageFactory(), r"""
        \documentclass{perftracker}
        \begin{document}
        """)
    ])
    def test_static_output(self, factory: LaTeXFactoryBase, expected_output: str) -> None:
        result = factory.generate(**self.args)

        self.assertEqual(result.strip(), expected_output.strip())
