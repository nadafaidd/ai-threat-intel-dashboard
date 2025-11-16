import streamlit as st
import pandas as pd
from core import feeds, rank, llm
from core.ui_effects import add_fireflies_background
from core.layout import add_top_links

add_top_links()

add_fireflies_background()
st.set_page_config(page_title="ATT&CK · AI Threat Intel", layout="wide")

# ----------------------------
# Load and Score Data
# ----------------------------
items = feeds.enrich_all(feeds.normalize_all(feeds.collect_all_sources()))
scored = rank.score_and_group(items)

# Expand the number of entries used
TOP_N = 15   # You can increase to 20, 30, or even ALL data
expanded_top = rank.select_top(scored, TOP_N)

# Generate ATT&CK mapping for more data
attack_map = llm.map_attack_techniques(expanded_top)

# ----------------------------
# Cybersecurity Advice / Policy of the Day
# ----------------------------
st.title("MITRE ATT&CK Mapping")

st.subheader("Cybersecurity Advice / Policy of the Day")

# GPT-powered fallback text (very short + professional)
advice_prompt = """
Provide ONE short practical cybersecurity advice suitable for an enterprise SOC.
It must be 1–2 sentences, actionable, and not generic.
Examples: "Enable MFA on VPN gateways", "Block legacy SMBv1 traffic", 
"Rotate API keys older than 90 days", "Audit admin privileges weekly", etc.
Return only the advice, no explanation.
"""

try:
    advice = llm.ask(advice_prompt).strip()
except:
    # Fallback if GPT unavailable
    advice = "Enable Multi-Factor Authentication (MFA) for all remote-access accounts and privileged users."

st.info(advice)

st.divider()

# ----------------------------
# ATT&CK Table (Expanded)
# ----------------------------
st.subheader(f"ATT&CK Mapping for Top {TOP_N} Threats")

if attack_map:
    df = pd.DataFrame(attack_map)

    # Show more rows by increasing height
    st.dataframe(df, use_container_width=True, height=700)
else:
    st.info("No techniques mapped yet.")
