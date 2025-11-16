import streamlit as st
from datetime import datetime
from core import feeds, rank, llm
import pandas as pd
from core.ui_effects import add_fireflies_background
import requests  # <-- for news API
from core.layout import add_top_links

add_top_links()

add_fireflies_background()

# -----------------------------
# SIDE PANELS (triggered by top links)
# -----------------------------
params = st.query_params

# ==================================================
# DEDICATED REPORT VIEW — MAXIMUM WIDTH (99%)
# ==================================================
if "report" in params:

    st.title("AI-Powered Threat Intel Dashboard")
    st.caption("Daily situational awareness: Top 5 threats · ATT&CK mapping · IoCs · Geo view")
    st.divider()

    # Super extra wide panel
    left, center, right = st.columns([0.005, 0.99, 0.005])

    with center:
        with st.container(border=True):
            st.markdown("### Report a Threat")

            with st.form("report_threat_form"):
                name = st.text_input("Your name")
                role = st.text_input("Role / Team")
                email = st.text_input("Contact email")
                org = st.text_input("Organization")
                details = st.text_area("Describe the threat or suspicious activity", height=220)
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                confirm = st.checkbox("I confirm this information is accurate.")
                submitted = st.form_submit_button("Submit Threat Report")

            if submitted:
                if confirm:
                    st.success("Your threat report has been recorded.")
                else:
                    st.error("Please confirm the information before submitting.")

    st.stop()



# ==================================================
# DEDICATED HELP VIEW — MAXIMUM WIDTH (99%)
# ==================================================
if "help" in params:

    st.title("AI-Powered Threat Intel Dashboard")
    st.caption("Daily situational awareness: Top 5 threats · ATT&CK mapping · IoCs · Geo view")
    st.divider()

    left, center, right = st.columns([0.005, 0.99, 0.005])

    with center:
        with st.container(border=True):
            st.markdown("### Ask for Help")

            with st.form("help_form"):
                name = st.text_input("Your name", key="h_name")
                email = st.text_input("Contact email", key="h_email")
                issue = st.text_area("Describe the issue you need help with", height=220)
                urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"], key="h_urgency")
                submitted_help = st.form_submit_button("Submit Help Request")

            if submitted_help:
                st.success("Your help request has been submitted.")

    st.stop()



st.title("AI-Powered Threat Intel Dashboard")
st.caption("Daily situational awareness: Top 5 threats · ATT&CK mapping · IoCs · Geo view")



# -----------------------------
# Helper: Fetch external cyber news
# -----------------------------
NEWS_API_KEY = "c18b947004944f7d80ac7c96cb79f564"  # <-- your key


def fetch_cybersecurity_news():
    """Fetch recent cybersecurity / cyberattack articles from NewsAPI."""
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWSAPI_KEY_HERE":
        return []

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": "cyber attack OR data breach OR ransomware OR cybersecurity",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
    }

    try:
        headers = {"X-Api-Key": NEWS_API_KEY}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])
    except Exception as e:
        print("Error fetching news:", e)
        return []


# -----------------------------
# Existing pipeline: Feeds, ranking, LLM
# -----------------------------

# Load data (mock or live collectors)
items_raw = feeds.collect_all_sources()
items = feeds.normalize_all(items_raw)
items = feeds.enrich_all(items)

# Scoring & selection
scored = rank.score_and_group(items)
top5 = rank.select_top(scored, k=5)

# LLM (optional) or templated summaries
top5_brief = llm.build_top5_brief(top5)
attack_map = llm.map_attack_techniques(top5)

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric(
    "Items Today",
    len(
        [
            x
            for x in items
            if x.get("published_at", "")[:10]
            == datetime.utcnow().strftime("%Y-%m-%d")
        ]
    ),
)
col2.metric("Unique CVEs", len({cve for it in items for cve in it.get("cve_list", [])}))
col3.metric("Sources", len(set([it["source"] for it in items])))

# -----------------------------
# New section: External Cybersecurity Articles
# -----------------------------
st.divider()
st.subheader("Latest Cybersecurity Headlines")

if NEWS_API_KEY == "YOUR_NEWSAPI_KEY_HERE":
    st.info(
        "Add your NewsAPI key in `Home_Dashboard.py` to load live cybersecurity articles."
    )
else:
    articles = fetch_cybersecurity_news()
    if not articles:
        st.warning("Could not load external cybersecurity news right now.")
    else:
        # Show first 4 as cards
        for article in articles[:4]:
            with st.container(border=True):
                c_img, c_text = st.columns([1, 2])

                with c_img:
                    img_url = article.get("urlToImage")
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.write("No preview image")

                with c_text:
                    st.markdown(f"### {article.get('title', 'Untitled article')}")
                    source = article.get("source", {}).get("name", "Unknown source")
                    published = article.get("publishedAt", "")
                    st.caption(f"{source} • {published}")
                    if article.get("description"):
                        st.write(article["description"])
                    st.markdown(
                        f"[Open full article]({article.get('url', '#')})"
                    )

# -----------------------------
# Existing section: Top 5 threats
# -----------------------------
st.divider()
st.subheader("Today's Top 5 (Auto-Ranked)")
for i, entry in enumerate(top5_brief, 1):
    with st.container(border=True):
        st.markdown(f"### {i}. {entry['title']}")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(entry["summary"])
            if entry.get("actions"):
                st.markdown("**Immediate actions:**")
                for act in entry["actions"]:
                    st.write(f"- {act}")
        with c2:
            st.markdown(f"**Risk:** `{entry['risk']}`")
            st.markdown(
                f"**Products:** {', '.join(entry.get('products', [])[:4])}"
            )
            st.markdown(
                f"**CVEs:** {', '.join(entry.get('cves', [])[:5])}"
            )

# -----------------------------
# Existing section: ATT&CK mapping
# -----------------------------
st.divider()
st.subheader("ATT&CK Mapping (for Top 5)")
if attack_map:
    df = pd.DataFrame(attack_map)
    st.dataframe(df, use_container_width=True, height=260)
else:
    st.info("No techniques mapped yet.")
