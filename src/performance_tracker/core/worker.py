import threading
from pathlib import Path

import pandas as pd

from performance_tracker.latex.compose import LaTeXComposer
from performance_tracker.latex.factories.chart_graph_factory import ChartGraphFactory
from performance_tracker.latex.factories.data_and_recommendations import (
    DataAndRecommendationsFactory,
)
from performance_tracker.latex.factories.full_width_rule_factory import (
    FullWidthRuleFactory,
)
from performance_tracker.latex.factories.new_page_factory import NewPageFactory
from performance_tracker.latex.factories.price_target_factory import PriceTargetFactory
from performance_tracker.latex.factories.section_heading_factory import (
    SectionHeadingFactory,
)


class Worker:
    def __init__(
        self, df: pd.DataFrame, config_dict: dict, output_dir: Path, shared_data: dict
    ) -> None:
        self.df = df
        self.config_dict: dict = config_dict
        self.output_dir = output_dir
        self.shared_data = shared_data

    def __call__(self) -> None:
        self._thread = threading.Thread(target=self.run_task, daemon=True)
        self._thread.start()

    def run_task(self) -> None:
        composer = LaTeXComposer(
            [
                SectionHeadingFactory(),
                ChartGraphFactory(),
                DataAndRecommendationsFactory(),
                PriceTargetFactory(),
                FullWidthRuleFactory(),
                NewPageFactory(),
            ]
        )

        composer(self.df, self.config_dict, self.output_dir)

        self.shared_data["done"] = True
        self.shared_data["is_running"] = False
        self.shared_data["reloaded"] = False

        print("...done!")
