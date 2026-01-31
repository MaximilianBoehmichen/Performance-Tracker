import textwrap

import pandas as pd
from yfinance import Ticker

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService
from performance_tracker.utils.maps import currency_to_latex_symbol
from performance_tracker.utils.short_number_rep import short_rep

PERFORMANCE_THRESHOLD = 50


class DataAndRecommendationsFactory(LaTeXFactoryBase):
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
        recommendations_latex = self.get_recommendations_bar_graph(
            ticker.recommendations
        )
        data_table_latex = self.get_data_table(
            ticker, combined_df, configdict.get("currency", "USD")
        )

        return textwrap.dedent(rf"""
        \noindent
        \begin{{minipage}}{{0.48\textwidth}}
            \centering
            {data_table_latex}
        \end{{minipage}}
        \hfill
        \begin{{minipage}}{{0.48\textwidth}}
            \centering
            {recommendations_latex}
        \end{{minipage}}
        \vspace{{1em}}

        """)

    @classmethod
    def get_recommendations_bar_graph(
        cls,
        recommendations: pd.DataFrame,
    ) -> str | None:
        if recommendations.empty:
            return "No recommendations available"

        current_recommendations = recommendations.iloc[0]
        cols = ["strongBuy", "buy", "hold", "sell", "strongSell"]
        value_counts = {col: current_recommendations.get(col, 0) for col in cols}
        legend_entries = {
            "hold": f"Hold ({value_counts["hold"]})",
            "buy": f"Buy ({value_counts["buy"]})",
            "strongBuy": f"Strong Buy ({value_counts["strongBuy"]})",
            "sell": f"Sell ({value_counts["sell"]})",
            "strongSell": f"Strong Sell ({value_counts["strongSell"]})",
        }

        total_recommendations_count = sum(value_counts.values())
        if total_recommendations_count == 0:
            return "No recommendations available"

        return textwrap.dedent(rf"""
        \begin{{tikzpicture}}
            \begin{{axis}}[
                title={{\textcolor{{mainColour}}{{\textbf{{Recommendations ({total_recommendations_count})}}}} }},
                width=\textwidth,
                height=4cm,
                xbar stacked,
                stack negative=separate,
                bar width=40pt,
                ymin=-0.2, ymax=0.2,
                axis lines=none,
                ticks=none,
                legend image code/.code={{
                    \draw[draw=none] (0cm,-0.1cm) rectangle (0.2cm,0.1cm);
                }},
                axis vline/.style={{
                    execute at end axis={{
                        \draw [thick, gray!50] (axis cs:0,-0.2) -- (axis cs:0,0.2);
                    }}
                }},
                axis vline,
                clip=false,
                legend style={{
                    at={{(0.5,-0.1)}},
                    anchor=north,
                    draw=none,
                    legend columns=2
                }}
            ]
            \addplot[fill=gray!50, draw=none, forget plot] coordinates {{(-{value_counts.get("hold", 0) / 2},0)}};
            \addplot[fill=gray!50, draw=none, forget plot] coordinates {{({value_counts.get("hold", 0) / 2},0)}};

            \addplot[fill=mainColour!50!black, draw=none, forget plot] coordinates {{({value_counts.get("buy", 0)},0)}};
            \addplot[fill=mainColour, draw=none, forget plot] coordinates {{({value_counts.get("strongBuy", 0)},0)}};

            \addplot[fill=red!50!black, draw=none, forget plot] coordinates {{(-{value_counts.get("sell", 0)},0)}};
            \addplot[fill=red, draw=none, forget plot] coordinates {{(-{value_counts.get("strongSell", 0)},0)}};

            \addlegendimage{{fill=red!50!black, draw=none}}
            \addlegendentry{{{legend_entries["sell"]}}}

            \addlegendimage{{fill=mainColour!50!black, draw=none}}
            \addlegendentry{{{legend_entries["buy"]}}}

            \addlegendimage{{fill=red, draw=none}}
            \addlegendentry{{{legend_entries["strongSell"]}}}


            \addlegendimage{{fill=mainColour, draw=none}}
            \addlegendentry{{{legend_entries["strongBuy"]}}}

            \end{{axis}}
        \end{{tikzpicture}}
        """)

    @classmethod
    def get_data_table(
        cls, ticker: Ticker, combined_df: pd.DataFrame, currency: str
    ) -> str:
        growth_estimate = ticker.growth_estimates
        cashflow = ticker.cashflow
        ticker_info = ticker.info

        cashflow.columns = pd.to_datetime(cashflow.columns)
        latest_date = cashflow.columns.max()

        growth = ""
        free_cash_flow = ""

        if not growth_estimate.empty:
            growth = rf"{growth_estimate.loc["+1y", "stockTrend"] * 100:.1f}\%"

        if not cashflow.empty:
            free_cash_flow = rf"{short_rep(cashflow.loc["Free Cash Flow", latest_date])} {currency_to_latex_symbol.get(currency, "USD")}"

        operating_cash_flow = rf"{short_rep(ticker_info.get("operatingCashflow", None))} {currency_to_latex_symbol.get(currency, "USD")}"
        enterprise_value = rf"{short_rep(ticker_info.get("enterpriseValue", None))} {currency_to_latex_symbol.get(currency, "USD")}"
        employees = rf"{short_rep(ticker_info.get("fullTimeEmployees", None))}"
        overall_risk = rf"{ticker_info.get("overallRisk", None)}"
        five_year_avg_dividend = rf"{short_rep(ticker_info.get("fiveYearAvgDividendYield", None))} {currency_to_latex_symbol.get(currency, "USD")}"
        beta = rf"{ticker_info.get("beta", None):.3f}"

        larger_than_reference_text = cls.get_percentage_larger(
            combined_df,
            first_col="Close_Adjusted",
            second_col="Close_Comparison_Adjusted",
        )
        larger_than_inflation_text = cls.get_percentage_larger(
            combined_df,
            first_col="Close_Adjusted",
            second_col="interpolated_inflation_adjusted",
        )

        return textwrap.dedent(rf"""
            \begin{{tabularx}}{{\textwidth}}{{p{{3.5cm}}R}}
                \textcolor{{mainColour}}{{\textbf{{Better than inflation:}}}} & {larger_than_inflation_text} \\
                \textcolor{{mainColour}}{{\textbf{{Better than reference:}}}} & {larger_than_reference_text} \\
            \end{{tabularx}}

            \vspace{{0.5cm}}\par

            \begin{{tabularx}}{{\textwidth}}{{p{{3.5cm}}R}}
                Growth Estimate: & {growth} \\
                Free Cash Flow: & {free_cash_flow} \\
                Operating Cash Flow: & {operating_cash_flow} \\
                Enterprise Value: & {enterprise_value} \\
            \end{{tabularx}}

            \vspace{{0.5cm}}\par

            \begin{{tabularx}}{{\textwidth}}{{p{{3.5cm}}R}}
                Employees: & {employees} \\
                Overall Risk: & {overall_risk} \\
                5-year $\varnothing$ Dividend: & {five_year_avg_dividend} \\
                Beta: & {beta} \\
            \end{{tabularx}}
        """)

    @classmethod
    def get_percentage_larger(
        cls, df: pd.DataFrame, first_col: str, second_col: str
    ) -> str:
        df_comp = df.dropna(subset=[first_col, second_col])

        count_larger_than = (df_comp[first_col] > df_comp[second_col]).sum()

        print(len(df_comp))

        total_comp = len(df_comp)
        percentage_larger_than = (count_larger_than / total_comp) * 100
        larger_than_color = (
            "mainColour" if percentage_larger_than >= PERFORMANCE_THRESHOLD else "red"
        )
        larger_than_textform = rf"\textcolor{{{larger_than_color}}}{{\textbf{{ {percentage_larger_than:.1f}\% }}}}"

        return larger_than_textform
