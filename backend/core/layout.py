import streamlit as st
import urllib.parse as urlparse

def add_top_links():
    """
    Adds right-aligned 'Quick actions: Report Threat | Ask Help' links.
    The links preserve current query params (like page=...) and just
    append ?report=1 or ?help=1 so the current page can open a panel.
    """

    # Build base query string from existing params (excluding old report/help)
    params = st.query_params
    pairs = []

    for key, values in params.items():
        if key in ("report", "help"):
            continue  # we will overwrite these
        # values may be list-like; handle both cases
        if isinstance(values, list):
            vals = values
        else:
            vals = [values]
        for v in vals:
            pairs.append(
                f"{urlparse.quote_plus(str(key))}={urlparse.quote_plus(str(v))}"
            )

    base_qs = "&".join(pairs)

    if base_qs:
        report_qs = base_qs + "&report=1"
        help_qs = base_qs + "&help=1"
    else:
        report_qs = "report=1"
        help_qs = "help=1"

    report_href = f"?{report_qs}"
    help_href = f"?{help_qs}"

    # --- UI + CSS ---
    st.markdown(
        f"""
        <style>
        .custom-top-links {{
            position: fixed;
            top: 48px;          /* below Streamlit's header */
            right: 55px;        /* tuned so it sits under 'Deploy' */
            z-index: 900;
            font-size: 13px;
            color: rgba(255,255,255,0.8);
            white-space: nowrap;
        }}
        .custom-top-links a {{
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            margin-left: 12px;
            font-weight: 500;
        }}
        .custom-top-links a:hover {{
            text-decoration: underline;
        }}
        </style>

        <div class="custom-top-links">
            Quick actions:
            <a href="{report_href}">Report Threat</a>
            <a href="{help_href}">Ask Help</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
