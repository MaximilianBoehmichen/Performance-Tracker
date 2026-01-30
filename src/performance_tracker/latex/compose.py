import random
import shutil
import subprocess
import textwrap
from pathlib import Path

import pandas as pd
import yfinance as yf

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.latex.factories.section_heading_factory import (
    SectionHeadingFactory,
)
from performance_tracker.latex.sidebar import Sidebar
from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService
from performance_tracker.services.ticker import get_tickers
from performance_tracker.utils.join import join_all_df

LATEX_RESOURCE_PATH = Path(__file__).parent / "resources"


class LaTeXComposer:
    def __init__(self, factories: list[LaTeXFactoryBase]) -> None:
        self._factories = factories
        self._exchange_rate_service = ExchangeRateService()
        self._inflation_service = InflationService()

    def __call__(self, df: pd.DataFrame, config_dict: dict, output_dir: Path) -> None:
        file_names = list()
        sidebar = Sidebar(df, self._exchange_rate_service, config_dict)

        for i in range(len(df)):
            row = df.iloc[i]
            ticker_info = {
                "symbol": row["Ticker"],
                "quantity": row["Quantity"],
                "buy_date": row["Purchase Date"],
                "sell_date": row["Sell Date"],
                "buy_price": row["Purchase Date"],
                "sell_price": row["Sell Price"],
            }

            if not ticker_info["symbol"]:
                continue

            file_name = ticker_info["symbol"] + str(random.randint(0, 2**32)) + ".tex"

            tickers = get_tickers(
                names=[
                    ticker_info["symbol"],
                    config_dict.get("comparison_ticker", "EUNL.DE"),
                ]
            )
            ticker, comparison_ticker = tickers[0], tickers[1]

            if not ticker:
                continue

            combined_df = join_all_df(
                comparison_ticker.info.get("currency"),
                comparison_ticker,
                config_dict,
                ticker.info.get("currency"),
                self._exchange_rate_service,
                self._inflation_service,
                ticker,
                config_dict.get("currency", "EUR"),
            )

            latex_output = self._iterate_factories(
                ticker_info,
                combined_df,
                ticker,
                comparison_ticker,
                config_dict,
                i,
                sidebar,
            )

            self.save_output(
                "\n".join(latex_output),
                file_name,
                output_dir,
            )

            file_names.append(file_name)

        self.copy_latex_cls(output_dir)
        self.create_main_tex(file_names, output_dir)
        self.render_latex(output_dir)

    def _generate(self, factory: LaTeXFactoryBase, **kwargs: object) -> str:
        print(f"at {factory}")
        try:
            return factory(**kwargs)
        except Exception:
            return "\n"

    def _iterate_factories(
        self,
        ticker_info: dict,
        combined_df: pd.DataFrame,
        ticker: yf.Ticker,
        comparison_ticker: yf.Ticker,
        config_dict: dict,
        index: int,
        sidebar: Sidebar,
    ) -> list[str]:
        latex_output = list()

        for factory in self._factories:
            output = self._generate(
                factory=factory,
                ticker_info=ticker_info,
                combined_df=combined_df,
                ticker=ticker,
                comparison_ticker=comparison_ticker,
                inflation_service=self._inflation_service,
                exchanger=self._exchange_rate_service,
                configdict=config_dict,
            )
            latex_output.append(output)

            if type(factory) is SectionHeadingFactory:
                latex_output.append(sidebar(index))

        return latex_output

    def save_output(self, output: str, filename: str, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / filename
        file_path.write_text(output, encoding="utf-8")

    def copy_latex_cls(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(LATEX_RESOURCE_PATH / "perftracker.cls", output_dir)

    def create_main_tex(self, file_names: list, output_dir: Path) -> None:
        content = textwrap.dedent(rf"""
        \documentclass{{perftracker}}

        \begin{{document}}

        {"\n".join([rf"\input{{{f}}}" for f in file_names])}

        \end{{document}}
        """)

        main_tex_path = output_dir / "main.tex"
        main_tex_path.write_text(content, encoding="utf-8")

    def render_latex(self, output_dir: Path) -> None:
        main_tex_path = output_dir / "main.tex"

        print(f"main_tex_path: {main_tex_path}")

        command = ["latexmk", "-pdf", "-interaction=nonstopmode", main_tex_path.name]

        try:
            subprocess.run(
                command,
                cwd=str(main_tex_path.parent),
                # capture_output=True,
                # text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print("Failed to render")
            print(f"STDOUT: {e.stdout}\n\n\n\n")
            print(f"STDERR: {e.stderr}")
