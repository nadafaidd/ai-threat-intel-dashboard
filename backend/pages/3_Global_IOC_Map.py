import os
from datetime import datetime

import pandas as pd
import streamlit as st

from core import feeds
from core.ui_effects import add_fireflies_background
from core.layout import add_top_links

add_top_links()

add_fireflies_background()


# ---------------------- Page Header ---------------------- #

st.title("Geo & IoCs")

st.write(
    """
    This page visualizes where recent Indicators of Compromise (IoCs) are located based on
    open-source threat intelligence feeds. The 3D globe below is a prototype view of global
    activity served by a separate React / Mapbox app.
    """
)

# ---------------------- React Globe Section (TOP) ---------------------- #

st.subheader("3D attack globe (React prototype)")

st.write(
    """
    The globe below is served by a separate Vite/React app that uses Deck.gl and Mapbox's
    `projection='globe'` mode. It currently animates simulated attack intensity per country,
    but it could be wired to real IoCs in the future.
    """
)

try:
    # Change the URL if your React app runs on another port.
    st.components.v1.iframe(
        src="http://localhost:5173",
        height=600,
        scrolling=False,
    )
except Exception:
    st.info(
        "React globe is not reachable. Make sure the `threat-map-frontend` app is running "
        "with `npm run dev` in a separate terminal."
    )

st.markdown("---")

# ---------------------- ThreatFox Fetch Controls (BELOW MAP) ---------------------- #

st.subheader("ThreatFox feed configuration")

threatfox_key_present = bool(os.environ.get("THREATFOX_AUTH_KEY"))

col_a, col_b = st.columns(2)
with col_a:
    days_back = st.number_input(
        "Look back (days)",
        min_value=1,
        max_value=60,
        value=7,
        step=1,
        help="How many days of ThreatFox data to pull.",
    )
with col_b:
    max_iocs = st.number_input(
        "Max IoCs to fetch",
        min_value=20,
        max_value=500,
        value=200,
        step=20,
        help="Upper limit on IoCs returned from ThreatFox.",
    )

# ---------------------- Fetch IoCs from ThreatFox ---------------------- #

threatfox_items_raw = feeds.fetch_threatfox_iocs(limit=int(max_iocs), days=int(days_back))
items = [feeds.normalize(it) for it in threatfox_items_raw]

st.caption(
    f"ThreatFox items loaded: {len(items)} "
    f"(THREATFOX_AUTH_KEY present: {threatfox_key_present})"
)

if not threatfox_key_present:
    st.warning(
        "No `THREATFOX_AUTH_KEY` detected in the environment. "
        "Set it with `setx THREATFOX_AUTH_KEY \"your_key_here\"`, "
        "restart the terminal, and relaunch the dashboard."
    )

# ---------------------- Indicators Table (BELOW CONFIG) ---------------------- #

st.subheader("Indicators")

ioc_rows = []

for item in items:
    src = item.get("source") or "ThreatFox"
    title = item.get("title") or ""
    ts_raw = item.get("published_at")

    try:
        ts = (
            datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            .strftime("%Y-%m-%d %H:%M")
            if ts_raw
            else ""
        )
    except Exception:
        ts = ts_raw or ""

    iocs = item.get("iocs", {}) or {}

    for value in iocs.get("ips", []):
        ioc_rows.append(
            {
                "Indicator": value,
                "Type": "IP",
                "Source": src,
                "When": ts,
                "Context": title,
            }
        )
    for value in iocs.get("domains", []):
        ioc_rows.append(
            {
                "Indicator": value,
                "Type": "Domain",
                "Source": src,
                "When": ts,
                "Context": title,
            }
        )
    for value in iocs.get("urls", []):
        ioc_rows.append(
            {
                "Indicator": value,
                "Type": "URL",
                "Source": src,
                "When": ts,
                "Context": title,
            }
        )
    for value in iocs.get("hashes", []):
        ioc_rows.append(
            {
                "Indicator": value,
                "Type": "Hash",
                "Source": src,
                "When": ts,
                "Context": title,
            }
        )

if not ioc_rows:
    st.info(
        "No IoCs in current items. If this persists:\n"
        "- Confirm that `THREATFOX_AUTH_KEY` is set and valid, and\n"
        "- Increase the look-back window (days) and the IoC limit above."
    )
else:
    df = pd.DataFrame(ioc_rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
