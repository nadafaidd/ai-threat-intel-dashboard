import streamlit as st
from core.ui_effects import add_fireflies_background
from core.layout import add_top_links

add_top_links()

add_fireflies_background()

st.set_page_config(page_title="Settings · AI Threat Intel", layout="wide")

st.title("Settings")
st.write("This starter keeps settings minimal. In a full deployment, this page can include fields for connecting provider keys, adjusting threat-scoring weights, and enabling data-redaction toggles..")
