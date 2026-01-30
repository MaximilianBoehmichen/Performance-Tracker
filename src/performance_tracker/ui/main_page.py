import time
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from performance_tracker.core.worker import Worker
from performance_tracker.utils.maps import COUNTRY_MAP, CURRENCY_MAP, PERIOD_MAP

MAX_INPUTS = 30

COLUMN_CONFIG = {
    "Ticker": st.column_config.TextColumn(
        "Ticker", width=100, help="The Ticker according to finance.yahoo.com"
    ),
    "Quantity": st.column_config.NumberColumn(
        "Quantity",
        width="small",
        help="How many shares are owned",
        min_value=1,
        max_value=1e100,
        step=1,
        format="localized",
    ),
    "Purchase Date": st.column_config.DateColumn(
        "Purchase Date",
        width="small",
        help="When this specific stock was purchased",
        min_value=date(1950, 1, 1),
        max_value=date.today(),
        format="localized",
    ),
    "Purchase Price": st.column_config.NumberColumn(
        "Purchase Price",
        width="small",
        help="At what price this specific stock was purchased, in the stock's currency",
        min_value=0,
        max_value=1e100,
        step=0.0001,
        format="accounting",
    ),
    "Sell Date": st.column_config.DateColumn(
        "Sell Date",
        width="small",
        help="When this specific stock was sold",
        min_value=date(1950, 1, 1),
        max_value=date.today(),
        format="localized",
    ),
    "Sell Price": st.column_config.NumberColumn(
        "Sell Price",
        width="small",
        help="At what price this specific stock was sold, in the stock's currency",
        min_value=0,
        max_value=1e100,
        step=0.0001,
        format="accounting",
    ),
}
DEFAULT_COLUMN_VALUES = {
    "Ticker": "",
    "Quantity": 0,
    "Purchase Date": pd.NaT,
    "Purchase Price": 0.0,
    "Sell Date": pd.NaT,
    "Sell Price": 0.0,
}

INTRO_TEXT = """Analyze the performance of different symbols against inflation and a local MSCI WORLD.
All values are adjusted for dividends and stock splits, so they might differ from the historic stock values.
"""


def get_input_as_csv() -> bytes:
    if "input_df" not in st.session_state:
        raise Exception("cannot find input_df")

    return st.session_state.input_df.to_csv(index=False).encode("utf-8")


def handle_upload() -> None:
    uploaded_file = st.session_state.csv_uploader
    if not uploaded_file:
        return

    if (
        "uploaded_file_id" not in st.session_state
        or st.session_state.uploaded_file_id != uploaded_file.file_id
    ):
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            required_columns = st.session_state.df.columns.tolist()

            missing_cols = [
                col for col in required_columns if col not in df_uploaded.columns
            ]

            if missing_cols:
                raise Exception(f"Missing columns: {missing_cols}")

            df_uploaded = df_uploaded[required_columns]
            df_uploaded = df_uploaded.fillna(DEFAULT_COLUMN_VALUES)

            st.session_state.df = df_uploaded
            st.session_state.uploaded_file_id = uploaded_file.file_id

        except Exception as e:
            st.error(f"Error reading uploaded CSV: {e}")


def start_analysis(currency: str, country: str, period: str) -> None:
    if not st.session_state.input_df["Ticker"].notna().any():
        return

    if len(st.session_state.input_df["Ticker"].notna()) > MAX_INPUTS:
        return

    if st.session_state.shared_data.get("is_running", False):
        return

    if "is_running" in st.session_state and st.session_state.is_running:
        return

    output_dir = (
        Path(__file__).parent.parent / "output" / f"{str(time.time()).replace(".", "")}"
    )

    worker = Worker(
        st.session_state.input_df,
        {
            "currency": CURRENCY_MAP.get(currency, "EUR"),
            "country": COUNTRY_MAP.get(country, "DEU"),
            "period": PERIOD_MAP.get(period, "1y"),
        },
        output_dir,
        st.session_state.shared_data,
    )

    worker()

    st.session_state.shared_data["done"] = False
    st.session_state.shared_data["is_running"] = True
    st.session_state.shared_data["progress_text"] = "starting..."
    st.session_state.shared_data["progress_percentage"] = 0
    st.session_state.shared_data["output_dir"] = output_dir


@st.fragment(run_every="5s")
def thread_status() -> None:
    if st.session_state.shared_data.get(
        "done", False
    ) and not st.session_state.shared_data.get("reloaded", True):
        print("reloading")
        st.session_state.shared_data["reloaded"] = True
        st.rerun()


def render_main_page() -> None:
    left_col, middle_col, right_col = st.columns([1, 3, 1], gap="medium")

    left_col.subheader(INTRO_TEXT)
    middle_col.subheader("Enter stock portfolio or upload it as CSV")
    right_col.subheader("Start analysis")

    if "shared_data" not in st.session_state:
        st.session_state.shared_data = dict()

    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(
            {
                "Ticker": pd.Series(dtype="str"),
                "Quantity": pd.Series(dtype="int"),
                "Purchase Date": pd.Series(dtype="datetime64[ns]"),
                "Purchase Price": pd.Series(dtype="float"),
                "Sell Date": pd.Series(dtype="datetime64[ns]"),
                "Sell Price": pd.Series(dtype="float"),
            }
        )

    st.session_state.input_df = middle_col.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        width="stretch",
        height="auto",
        column_config=COLUMN_CONFIG,
        hide_index=True,
        key="input_editor",
    )

    middle1_col, middle2_col, middle3_col = middle_col.columns([2, 1, 2], gap="medium")
    middle1_col.file_uploader(
        label="Upload from CSV",
        type="csv",
        accept_multiple_files=False,
        on_change=handle_upload,
        key="csv_uploader",
    )
    middle2_col.markdown("or save current input:")
    middle3_col.download_button(
        label="Download as CSV",
        data=st.session_state.input_df.to_csv(index=False).encode("utf-8"),
        file_name=f"portfolio_data-{pd.Timestamp.now()}.csv",
        mime="text/csv",
    )

    thread_status()

    with right_col.form("Settings"):
        period = st.selectbox("Duration", ["2 years", "5 years", "10 years"])
        country = st.selectbox("Inflation of", ["Germany"])
        currency = st.selectbox("Currency", ["Euro"])
        submitted = st.form_submit_button(
            "Generate",
            icon="spinner"
            if st.session_state.shared_data.get("is_running", False)
            else None,
        )

        if submitted:
            start_analysis(currency, country, period)
            st.rerun()

    if st.session_state.shared_data.get("is_running", False):
        right_col.success("Analysis is being generated!")
        progress_text = st.session_state.shared_data.get("progress_text", "")
        right_col.progress(0, text=progress_text)

    pdf_path = st.session_state.shared_data.get("output_dir", Path()) / "main.pdf"
    if (
        st.session_state.shared_data.get("done", False)
        and pdf_path.exists()
        and st.session_state.shared_data.get("done", False)
    ):
        with Path.open(pdf_path, "rb") as f:
            right_col.download_button(
                label="Download :dollar::dollar::dollar:",
                data=f,
                file_name="report.pdf",
                mime="application/pdf",
            )
