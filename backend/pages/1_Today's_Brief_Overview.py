import streamlit as st
import pandas as pd
from collections import Counter
from core import feeds, rank, llm, export
from core.ui_effects import add_fireflies_background
from core.layout import add_top_links

add_top_links()

# Page config
st.set_page_config(page_title="Today's Brief · AI Threat Intel", layout="wide")

add_fireflies_background()

# -----------------------------
# Load & process feed data
# -----------------------------
items = feeds.enrich_all(
    feeds.normalize_all(
        feeds.collect_all_sources()
    )
)
scored = rank.score_and_group(items)
top5 = rank.select_top(scored, 5)
brief = llm.build_top5_brief(top5)

# -----------------------------
# Page title
# -----------------------------
st.title("Today's Brief")

# =====================================================
# 🔥 Trending Threat Actors  (AT THE TOP NOW)
# =====================================================
st.divider()
st.subheader("Trending Threat Actors")

# Known actor patterns
KNOWN_ACTORS = {
    "Lazarus Group": ["lazarus"],
    "APT41": ["apt41", "apt-41"],
    "FIN7": ["fin7", "fin 7"],
    "APT28 (Fancy Bear)": ["apt28", "apt-28", "fancy bear"],
    "APT29 (Cozy Bear)": ["apt29", "apt-29", "cozy bear"],
    "Conti": ["conti"],
    "LockBit": ["lockbit"],
    "REvil": ["revil", "sodinokibi"],
}

actor_counts = Counter()

# Scan titles + descriptions + summaries
for it in items:
    text = " ".join(
        [
            str(it.get("title", "")),
            str(it.get("description", "")),
            str(it.get("summary", "")),
        ]
    ).lower()

    for actor_name, patterns in KNOWN_ACTORS.items():
        if any(pat in text for pat in patterns):
            actor_counts[actor_name] += 1

if not actor_counts:
    st.info("No recognizable threat actor names detected in today's items.")
else:
    top_actors = actor_counts.most_common(3)
    arrows = ["↑", "↑", "↓"]  # simple visual trend

    for (actor_name, count), arrow in zip(top_actors, arrows[: len(top_actors)]):
        st.write(f"- **{actor_name}** {arrow}  ({count} mentions)")

# =====================================================
# Existing Top 5 Threat Summary
# =====================================================
st.divider()
st.subheader("Top 5 Cyber Threats Today")

for i, entry in enumerate(brief, 1):
    with st.container(border=True):
        st.markdown(f"### {i}. {entry['title']}")
        st.write(entry["summary"])
        st.caption(
            f"Risk: {entry['risk']} | CVEs: {', '.join(entry.get('cves', [])) or '—'}"
        )

# =====================================================
# Export Section
# =====================================================
st.divider()
if st.button("Export Markdown"):
    md = export.to_markdown(brief)
    st.download_button(
        label="Download Daily Brief.md",
        data=md,
        file_name="daily_threat_brief.md"
    )
