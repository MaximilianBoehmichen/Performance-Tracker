import datetime
import textwrap

import pandas as pd

from performance_tracker.services.exchange_rate import ExchangeRateService
from performance_tracker.services.ticker import get_tickers
from performance_tracker.utils.maps import (
    currency_to_latex_symbol_table,
)
from performance_tracker.utils.short_number_rep import short_rep


class Sidebar:
    def __init__(
        self,
        df: pd.DataFrame,
        exchange_rate_service: ExchangeRateService,
        config_dict: dict,
    ) -> None:
        self._df = df
        self._exchange_rate_service = exchange_rate_service
        self._config_dict = config_dict
        self._overview_table: list[tuple[int, str, float, float]] = list()
        self._generated = f"Generated: {datetime.datetime.now().strftime("%d.%m.%Y")}"

        self._prepare_overview_table()

    def __call__(self, index: int) -> str:
        row = self._df.iloc[index]
        ticker_data = {
            "symbol": row["Ticker"],
            "quantity": row["Quantity"],
        }

        ticker = get_tickers(ticker_data["symbol"])[0]
        ticker_info = ticker.info

        name = ticker_info.get("longName", "").replace("&", r"\&")
        position_type = ticker_info.get("quoteType", "Equity")
        country = ticker_info.get("country", "")
        symbol = ticker_info.get("symbol", "")
        sector = ticker_info.get("sector", "")
        currency = ticker_info.get("currency", "USD")
        quantity = ticker_data["quantity"]
        close = ticker_info.get("previousClose", "")

        dividend_yield = ticker_info.get("dividendYield", 0.0)
        dividend = ticker_info.get("dividendRate", 0.0)

        return self._latex_template(
            name,
            position_type,
            country,
            symbol,
            sector,
            currency,
            quantity,
            close,
            dividend_yield,
            dividend,
            index,
        )

    def _prepare_overview_table(self) -> None:
        self._total_value = 0

        for i in range(len(self._df)):
            row = self._df.iloc[i]
            ticker_data = {
                "symbol": row["Ticker"],
                "quantity": row["Quantity"],
            }

            if not ticker_data["symbol"]:
                self._overview_table.append((i, "", 0.0, 0))
                continue

            ticker = get_tickers(ticker_data["symbol"])[0]
            ticker_info = ticker.info

            value = (
                ticker_data["quantity"]
                * self._exchange_rate_service.get_latest_exchange_rate(
                    ticker_info.get("currency", "USD"), self._config_dict["currency"]
                )
                * ticker_info["previousClose"]
            )

            self._total_value += value
            self._overview_table.append((i, ticker_data["symbol"], 0.0, value))

        self._overview_table = [
            (index, name, value / self._total_value, value)
            for index, name, percentage, value in self._overview_table
        ]

    def _table_for_index(self, index: int) -> str:
        to_currency_symbol = currency_to_latex_symbol_table.get(
            self._config_dict.get("currency", ""), "USD"
        )

        entries = [
            (
                (
                    rf"{self._overview_table[i][1][:7]}"
                    rf" & {100 * self._overview_table[i][2]:.2f}"
                    rf" & {short_rep(self._overview_table[i][3]) + " " + to_currency_symbol}"
                    + r" \\"
                    + "\n"
                )
                if i != index
                else (
                    rf"\textbf{{{self._overview_table[i][1][:7]}}}"
                    rf" & \textbf{{{100 * self._overview_table[i][2]:.2f}}}"
                    rf" & \textbf{{{short_rep(self._overview_table[i][3]) + " " + to_currency_symbol}}}"
                    + r"\\"
                    + "\n"
                )
            )
            if self._overview_table[i][1]
            else None
            for i in range(len(self._overview_table))
        ]

        return "\n".join([entry for entry in entries if entry is not None])

    def _latex_template(
        self,
        name: str,
        position_type: str,
        country: str,
        symbol: str,
        sector: str,
        currency: str,
        quantity: str,
        close: str,
        dividend_yield: str,
        dividend: str,
        index: int,
    ) -> str:
        return textwrap.dedent(rf"""
        \setsidebar{{
            {{\bfseries
            Current Position: \\[0pt]
            \textcolor{{mainColour}}{{ {name} }} \par}}

            \vspace{{0.5cm}}

            \begin{{tabularx}}{{\linewidth}}{{p{{2.25cm}}X}}
              Type: & {position_type} \\
              Country & {country} \\
              Symbol: & {symbol} \\
              Sector: & {sector} \\
              Currency: & {currency} \\
              Quantity: & {quantity} \\
              Close: & \textcolor{{mainColour}}{{\textbf{{{f"{close:.2f}" + " " + currency_to_latex_symbol_table.get(currency, "USD")}}}}} \\
            \end{{tabularx}}

            \vspace{{0.5cm}}\par

            \begin{{tabularx}}{{\linewidth}}{{p{{2.25cm}}X}}

              Dividend Yield: & {dividend_yield}\% p.a.\\
              Dividend: & {f"{dividend:.2f}" + " " + currency_to_latex_symbol_table.get(currency, "USD")}
            \end{{tabularx}}


            \vspace{{0.5cm}}
            \noindent{{\color{{black}}\rule{{\linewidth}}{{1pt}}}}\par
            \vspace{{0.5cm}}

            \noindent
            \begin{{tabularx}}{{\linewidth}}{{
              X
              >{{\raggedleft\arraybackslash}}p{{1.0cm}}
              >{{\raggedleft\arraybackslash}}p{{1.4cm}}
            }}
                {{\textcolor{{mainColour}}{{\textbf{{Position}}}}}}
                & {{\textcolor{{mainColour}}{{\textbf{{\%}}}}}}
                & {{\textcolor{{mainColour}}{{\textbf{{Value}}}}}} \\
                \midrule
                {self._table_for_index(index)}
                \bottomrule
                Total: & \multicolumn{{2}}{{r}}{{ {short_rep(self._total_value) + " " + currency_to_latex_symbol_table.get(self._config_dict.get("currency", ""), "USD")} }}
            \end{{tabularx}}

            \vspace{{0.5cm}}
            \noindent{{\color{{black}}\rule{{\linewidth}}{{1pt}}}}\par
            \vspace{{0.5cm}}
            \noindent
            {self._generated}
        }}
        """)
