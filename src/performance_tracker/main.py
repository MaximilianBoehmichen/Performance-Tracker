import streamlit as st
from dotenv import load_dotenv
from ui.main_page import render_main_page

load_dotenv()

st.set_page_config(
    page_title="Performance Tracker",
    page_icon=":dollar:",
    layout="wide",
)

st.title("Performance Tracker")
render_main_page()
