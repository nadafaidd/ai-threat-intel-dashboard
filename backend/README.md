# AI Threat Intel Dashboard (Starter)

A Streamlit dashboard that aggregates threat-intel feeds, ranks items, maps to MITRE ATT&CK,
and produces a concise "Top 5" daily brief. This starter uses **mock data** so you can run it
immediately; then you can plug in real collectors (CISA RSS, NVD API, CERTs, etc.).

## Quick Start
1. Create a virtual env (optional) and install deps:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. Open the browser link shown in the terminal.

## Enabling LLM Summaries (optional)
- Set `OPENAI_API_KEY` in your environment to enable LLM-based Top-5 and ATT&CK mapping.
  By default, the app will generate **template summaries** without calling external APIs.

## Project Structure
```
threat_intel_dashboard/
  app.py
  core/
    feeds.py        # (stubs) collectors for CISA/NVD/etc. + mock loader
    normalize.py    # raw item -> canonical schema
    enrich.py       # IoC extraction, CVSS lookups (stub), ATT&CK rule mapping
    rank.py         # ranking & dedup logic
    llm.py          # Top-5 + ATT&CK prompts (LLM optional)
    export.py       # export daily brief to Markdown
  data/
    sample_feeds.json  # mock items you can extend
    attack_rules.json  # keyword -> technique mapping
  pages/
    1_Today.py
    2_ATT&CK.py
    3_Geo_IoCs.py
    4_All_Feeds.py
    5_Settings.py
  assets/
    logo.txt
  .streamlit/
    config.toml
  requirements.txt
  README.md
```

## Evaluation (suggested)
- **Primary:** precision@3 overlap vs. CISA’s key advisories for a test window.
- **Secondary:** readability/usefulness survey (Likert 1–5) for the daily brief.
- **Ablation:** compare ranks without duplication score / without CVSS.

## Next Steps
- Implement real collectors in `core/feeds.py`.
- Replace mock LLM calls in `core/llm.py` with actual API calls.
- Add geo parsing for more accurate map placement.
- Expand ATT&CK mapping rules in `data/attack_rules.json`.
