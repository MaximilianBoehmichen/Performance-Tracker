import textwrap

import pandas as pd
from yfinance import Ticker

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase
from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.inflation import InflationService
from performance_tracker.services.ticker import get_tickers
from performance_tracker.utils.join import join_all_df
from performance_tracker.utils.maps import currency_to_latex_symbol


class PriceTargetFactory(LaTeXFactoryBase):
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
        currency = ticker.info.get("currency", "USD")
        price_targets = ticker.analyst_price_targets
        current = ticker.info.get("previousClose", 0)
        high = price_targets.get("high", None)
        low = price_targets.get("low", None)
        mean = price_targets.get("mean", None)
        median = price_targets.get("median", None)

        maximum = max([x for x in [current, high, low] if x is not None], default=0)
        minimum = max(
            min([x for x in [current, high, low] if x is not None], default=0), 0
        )
        width = maximum - minimum

        if width == 0:
            display_width = 1
            offset = current - display_width / 2
        else:
            display_width = 1.25 * width
            offset = minimum - 0.125 * width

        min_draw = self.get_target_rep(
            current,
            minimum,
            offset,
            "black",
            rf"Min: {minimum:.2f} {currency_to_latex_symbol.get(currency, r"\$")}",
        )
        max_draw = self.get_target_rep(
            current,
            maximum,
            offset,
            "black",
            rf"Max: {maximum:.2f} {currency_to_latex_symbol.get(currency, r"\$")}",
        )
        mean_draw = self.get_target_rep(current, mean, offset, "red", "")
        median_draw = self.get_target_rep(
            current, median, offset, "mainColour!50!black", ""
        )
        mean_legend = textwrap.dedent(r"""
            \draw[red, line width=0.1cm] (0, -1.0) -- (0.4cm, -1.0);
            \node[right] at  (0.5cm, -1.0cm) {Mean Analyst Price Target};

        """)
        median_legend = textwrap.dedent(r"""
            \draw[mainColour!50!black, line width=0.1cm] (5cm, -1.0) -- (5.4cm, -1.0);
            \node[right] at  (5.5cm, -1.0cm) {Median Analyst Price Target};

        """)

        return textwrap.dedent(rf"""
        \noindent%
            \begin{{tikzpicture}}[x=\textwidth/{display_width}, y=1cm]
                \path[use as bounding box] (0, -1.2) rectangle ({display_width}, 0.6);
                \fill[gray!50] (0,0) rectangle ({display_width}, 0.2);

                \draw[mainColour, line width=0.1cm] ({current - offset}, -0.1) -- ({current - offset}, 0.3);
                \node[above] at ({current - offset}, 0.35) {{ \textcolor{{mainColour}}{{Currently: {current:.2f} {currency_to_latex_symbol.get(currency, r"\$")} }} }};

                {min_draw}
                {max_draw}
                {mean_draw}
                {median_draw}

                {mean_legend if mean else ""}
                {median_legend if mean else ""}

            \end{{tikzpicture}}
            """)

    @classmethod
    def get_target_rep(
        cls,
        current: float | None,
        target: float | None,
        offset: float | None,
        colour: str,
        text: str,
    ) -> str:
        if not (current and target and offset):
            return ""

        draw = ""
        if target != current:
            draw = textwrap.dedent(rf"""
                \draw[{colour}, line width=0.1cm] ({target - offset}, -0.1) -- ({target - offset}, 0.3);
                \node[below] at ({target - offset}, -0.1) {{ \textcolor{{{colour}}}{{ {text} }} }};
            """)
        return draw


if __name__ == "__main__":
    import pandas as pd

    config_dict = {
        "currency": "EUR",
        "country": "DEU",
        "period": "10y",
    }

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)

    cgf = PriceTargetFactory()

    ticker = get_tickers(names="SAP.DE")[0]

    comparison_ticker: Ticker = get_tickers(names="EUNL.DE")[0]
    inflation_service = InflationService()
    exchanger = ExchangeRateService()
    combined_df = join_all_df(
        comparison_ticker.info.get("currency"),
        comparison_ticker,
        config_dict,
        ticker.info.get("currency"),
        exchanger,
        inflation_service,
        ticker,
        "EUR",
    )

    ret = cgf.generate(
        ticker_info={
            "symbol": "SAP.DE",
            "quantity": 2,
            "buy_date": "",
            "sell_date": "",
            "buy_price": 0,
            "sell_price": 0,
        },
        combined_df=combined_df,
        ticker=ticker,
        comparison_ticker=comparison_ticker,
        inflation_service=inflation_service,
        exchanger=exchanger,
        configdict=config_dict,
    )

    print(ret)
