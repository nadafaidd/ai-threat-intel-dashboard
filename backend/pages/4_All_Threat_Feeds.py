import streamlit as st
import pandas as pd
from core import feeds, rank
from core.ui_effects import add_fireflies_background
from core.layout import add_top_links

add_top_links()

add_fireflies_background()

st.set_page_config(page_title="All Feeds · AI Threat Intel", layout="wide")

items = feeds.enrich_all(feeds.normalize_all(feeds.collect_all_sources()))
scored = rank.score_and_group(items)

st.title("All Feeds")
df = pd.DataFrame(scored)
st.dataframe(df[["source","published_at","title","cvss_max","rank_score","cve_list","products"]], use_container_width=True, height=600)
