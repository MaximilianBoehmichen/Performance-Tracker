import textwrap
from datetime import datetime

import pandas as pd
from yfinance import Ticker

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService
from performance_tracker.utils.calc_df import total_minmax
from performance_tracker.utils.maps import currency_to_latex_symbol

BASE_LEVEL = 100


class ChartGraphFactory(LaTeXFactoryBase):
    def generate(
        self,
        ticker_info: dict,
        combined_df: pd.DataFrame,
        ticker: Ticker,
        comparison_ticker: Ticker,
        inflation_service: InflationService,
        exchanger: ExchangeRateService,
        configdict: dict | None = None,
    ) -> str:
        last_price = ticker.info.get("previousClose", None)

        start_date = combined_df.index[0].replace(tzinfo=None)
        end_date = combined_df.index[-1].replace(tzinfo=None)
        min_val, max_val = total_minmax(
            combined_df[
                [
                    "Close_Adjusted",
                    "interpolated_inflation_adjusted",
                    "Close_Comparison_Adjusted",
                ]
            ]
        )
        xticks, xticklabels = self.get_xticks(
            start_date, end_date, configdict.get("period", None)
        )
        graph_min = f"{min_val - 0.05 * (max_val - min_val):.2f}"
        graph_max = f"{max_val + 0.05 * (max_val - min_val):.2f}"

        return textwrap.dedent(rf"""
        \begin{{center}}
        \resizebox{{\textwidth}}{{!}}{{%
            \begin{{tikzpicture}}
                \begin{{axis}}[
                    width=0.9\textwidth,
                    height=8cm,
                    date coordinates in=x,
                    date ZERO={start_date.strftime('%Y-%m-%d')},
                    xmin={start_date.strftime('%Y-%m-%d')}, xmax={end_date.strftime('%Y-%m-%d')},
                    ymin={graph_min}, ymax={graph_max},
                    tick label style={{font=\footnotesize\sffamily, color=black}},
                    xticklabels={{ {xticklabels} }},
                    xtick={{ {xticks} }},
                    {self.get_extra_xticks(ticker.dividends, start_date)},
                    extra x tick style={{
                        tick pos=lower,
                        major tick length=5pt,
                        tick style={{green!70!black, ultra thick}},
                    }},
                    yticklabel={{\pgfmathprintnumber{{\tick}}\%}},
                    yticklabel style={{
                        /pgf/number format/fixed,
                        /pgf/number format/precision=0,
                        /pgf/number format/assume math mode=true,
                    }},
                    ymajorgrids=true,
                    extra y ticks={{ {combined_df["Close_Adjusted"].iloc[-1]} }},
                    extra y tick labels={{ {self.get_percent_performance(combined_df, "Close_Adjusted")} }},
                    extra y tick style={{
                        tick pos=right,
                        yticklabel pos=right,
                        draw=none,
                    }},
                    tick pos=lower,
                    legend style={{
                        at={{(axis description cs:0, 1.025)}},
                        anchor=south west,
                        draw=none,
                        fill=none,
                        legend columns=-1,
                        inner sep=0pt,
                    }},
                    grid style={{dotted, black}},
                    clip=false,
                ]
                \addplot[
                    red,
                    thin,
                    ] coordinates {{
                    {self.get_datapoints(combined_df, "interpolated_inflation_adjusted")}
                }};
                \addlegendentry{{Inflation}}
                \addplot[
                    green,
                    thin,
                    ] coordinates {{
                    {self.get_datapoints(combined_df, "Close_Comparison_Adjusted")}
                }};
                \addlegendentry{{ {comparison_ticker.info.get("symbol", "Reference")} }}
                \addplot[
                    mainColour,
                    thick,
                    ] coordinates {{
                    {self.get_datapoints(combined_df, "Close_Adjusted")}
                }};
                %\addlegendentry{{Adjusted Value}}
                \node[anchor=south east] at (axis description cs:1, 1.025)
                    {{ \textcolor{{mainColour}}{{ \textbf{{ {last_price:.2f} {currency_to_latex_symbol.get(ticker.info["currency"], "")} }} }} on {end_date.strftime("%d.%m.%Y")} }};
                \end{{axis}}
            \end{{tikzpicture}}%
            }}
            \end{{center}}
        """)

    @classmethod
    def get_xticks(
        cls, start_date: datetime, end_date: datetime, period: str
    ) -> tuple[str, str]:
        xticks: list[str] = []
        xticklabels: list[str] = []

        print(f"selected period: {period}")

        if period == "10y":
            end_year = end_date.year
            for i in range(10):
                xticks.append(f"{end_year - i}-01-01")
                if i % 2 == 0:
                    xticklabels.append(f"Jan {end_year - i}")
                else:
                    xticklabels.append("")

        elif period == "5y":
            end_year = end_date.year
            for i in range(5):
                xticks.append(f"{end_year - i}-01-01")
                xticklabels.append(f"Jan {end_year - i}")

        elif period in {"2y", "1y"}:
            pass

        return ", ".join(xticks), ", ".join(xticklabels)

    @classmethod
    def get_extra_xticks(cls, df: pd.Series, start_date: datetime) -> str:
        if df.empty or not isinstance(df.index, pd.DatetimeIndex):
            return ""

        start_date = pd.Timestamp(start_date)

        tick_dates = (
            df.index[df.index >= start_date.tz_localize(df.index.tz)]
            .strftime("%Y-%m-%d")
            .tolist()
        )
        ticks = f"extra x ticks={{ {", ".join(tick_dates) } }}"
        labels = f"extra x tick labels={{ {"," * (len(tick_dates) - 1)} }}"

        return ",\n".join([ticks, labels])

    @classmethod
    def get_datapoints(cls, df: pd.DataFrame, val_col: str) -> str:
        datapoints = [
            f"({dt.strftime("%Y-%m-%d")}, {val})" for dt, val in df[val_col].items()
        ]

        return "\n\t\t\t\t\t".join(datapoints)

    @classmethod
    def get_percent_performance(cls, df: pd.DataFrame, val_col: str) -> str:
        last_performance = df[val_col].iloc[-1]

        if last_performance >= BASE_LEVEL:
            return rf"\textcolor{{green!70!black}}{{ \textbf{{ +{last_performance - BASE_LEVEL:.2f}\% }}}}"
        else:
            return rf"\textcolor{{red!70!black}}{{ \textbf{{ -{BASE_LEVEL - last_performance:.2f}\% }}}}"
