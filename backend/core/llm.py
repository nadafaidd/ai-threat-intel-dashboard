import os, json, textwrap

# Optional: real LLM client (OpenAI). If this import fails, the dashboard will
# still work using the fallback templated summaries below.
try:
    from openai import OpenAI  # pip install openai
except ImportError:  # handled at runtime
    OpenAI = None

# You can override the model with an env var, e.g. OPENAI_MODEL=gpt-5.1
# The default here uses a small, fast model that is good for summaries.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def _get_client():
    """
    Returns an OpenAI client if OPENAI_API_KEY is configured and the
    'openai' package is installed; otherwise returns None so the
    rest of the module can gracefully fall back to local logic.
    """
    if OpenAI is None:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        # The OpenAI Python SDK reads OPENAI_API_KEY from the environment.
        # See docs: client = OpenAI(); client.responses.create(...).
        # https://platform.openai.com/docs/overview?lang=python
        return OpenAI()
    except Exception:
        # Any error creating the client -> behave as if LLM is disabled.
        return None


def _template_summary(item):
    """Fallback non-LLM summary used when GPT is unavailable.

    This keeps the dashboard functional offline or without API keys.
    """
    title = item.get("title", "Untitled")
    products_str = ", ".join(item.get("products", [])[:3]) or "General"
    cves_str = ", ".join(item.get("cve_list", [])[:3]) or "—"
    risk = (
        "High"
        if item.get("cvss_max", 0) >= 9
        else "Medium"
        if item.get("cvss_max", 0) >= 7
        else "Low"
    )
    summary = item.get("summary", "") or (
        f"{title}. Affected: {products_str}. CVEs: {cves_str}. "
        "Prioritize review and patching if applicable."
    )

    actions = []
    if item.get("cve_list"):
        actions.append("Review CVEs and apply available patches")
    if item.get("iocs", {}).get("domains"):
        actions.append("Blocklisted domains in perimeter controls")
    actions.append("Add detection rule to SIEM/EDR based on indicators")

    return {
        "title": title,
        "summary": summary[:600],
        "risk": risk,
        "products": item.get("products", []),
        "cves": item.get("cve_list", [])[:5],
        "actions": actions,
    }


def _serialize_item_for_llm(it):
    """Prepare a compact JSON-safe version of a threat item for the LLM."""
    return {
        "id": it.get("id"),
        "source": it.get("source"),
        "title": it.get("title"),
        "published_at": it.get("published_at"),
        "cvss_max": it.get("cvss_max"),
        "products": it.get("products", []),
        "cve_list": it.get("cve_list", []),
        # Truncate long blobs so we don't blow up token usage
        "summary": (it.get("summary") or "")[:1500],
        "description": (it.get("description") or "")[:1500],
        "iocs": it.get("iocs", {}),
    }


def _summarize_with_gpt(items):
    """
    Ask GPT to turn the raw feed items into short SOC-friendly summaries.

    Returns a list of dicts with the same shape as _template_summary().
    On any error it returns None so the caller can fall back.
    """
    client = _get_client()
    if client is None:
        return None

    # Build the JSON payload the model will see
    payload = {"items": [_serialize_item_for_llm(it) for it in items]}

    system_prompt = (
        "You are powering a cyber attack awareness dashboard for SOC analysts.\n"
        "You receive a JSON array of up to 5 threat items under the key 'items'.\n"
        "For EACH item, generate a concise summary that is:\n"
        "- Focused on what is impacted and how an attacker would abuse it.\n"
        "- Easy to skim in <3 sentences.\n"
        "- Free of marketing/fluff.\n\n"
        "For each item, output an object with these keys:\n"
        "- title: short human-readable title (string).\n"
        "- risk: one of Critical, High, Medium, Low.\n"
        "- summary: <=3 sentences plain text.\n"
        "- products: array of up to 4 key affected products/technologies.\n"
        "- cves: array of up to 5 relevant CVE IDs.\n"
        "- actions: array of 2–4 short SOC actions (verbs first, imperative).\n\n"
        "Return ONLY valid JSON with this shape (no extra commentary):\n"
        "{ \"items\": [ { ... }, ... ] }"
    )

    user_prompt = (
        "Use this JSON as your input and follow the instructions above.\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        # Using the Responses API (Python SDK):
        # response = client.responses.create(model=..., input=...)
        # https://platform.openai.com/docs/guides/text
        resp = client.responses.create(
            model=DEFAULT_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        # With response_format=json_object the SDK exposes JSON as text.
        raw = resp.output_text  # type: ignore[attr-defined]
        data = json.loads(raw)
    except Exception:
        # Any problem with the API or JSON parsing -> signal failure.
        return None

    results = []
    generated_items = data.get("items", []) if isinstance(data, dict) else []
    for original, gen in zip(items, generated_items):
        # Start from the deterministic template and then layer GPT output on top
        base = _template_summary(original)
        if isinstance(gen, dict):
            base["title"] = gen.get("title", base["title"]) or base["title"]
            base["risk"] = gen.get("risk", base["risk"]) or base["risk"]

            if gen.get("summary"):
                base["summary"] = textwrap.shorten(
                    str(gen["summary"]),
                    width=550,
                    placeholder="…",
                )

            if isinstance(gen.get("products"), list) and gen["products"]:
                base["products"] = gen["products"][:4]

            if isinstance(gen.get("cves"), list) and gen["cves"]:
                base["cves"] = gen["cves"][:5]

            if isinstance(gen.get("actions"), list) and gen["actions"]:
                base["actions"] = [str(a) for a in gen["actions"][:6]]

        results.append(base)

    # If GPT returned fewer entries than we sent, fill the rest with templates
    if len(results) < len(items):
        for it in items[len(results) :]:
            results.append(_template_summary(it))

    return results


def build_top5_brief(top5_items):
    """Main entrypoint used by app.py.

    Tries GPT first (if configured), otherwise falls back to static summaries.
    """
    # Try live GPT summaries
    llm_results = _summarize_with_gpt(top5_items)
    if llm_results is not None:
        return llm_results

    # Fallback for offline / no key / errors
    return [_template_summary(it) for it in top5_items]


def map_attack_techniques(items):
    """Lightweight ATT&CK mapping.

    This still uses a simple keyword heuristic. If you want, you can extend this
    to call GPT in a similar way to _summarize_with_gpt and ask it to propose
    ATT&CK technique IDs, but keeping it static here avoids extra token usage.
    """
    out = []
    for it in items:
        title = (it.get("title", "") + " " + it.get("summary", "")).lower()
        mapped = []

        if any(k in title for k in ["phish", "social engineering", "credential"]):
            mapped.append(("T1566", 0.7, "phishing / credential harvesting indicators"))

        if any(k in title for k in ["command injection", "rce", "remote code execution"]):
            mapped.append(("T1059", 0.8, "remote command execution patterns"))

        if any(k in title for k in ["brute", "password spray", "credential stuffing"]):
            mapped.append(("T1110", 0.6, "authentication brute-force activity"))

        if "ransom" in title:
            mapped.append(("T1486", 0.7, "ransomware / data encryption behavior"))

        if not mapped:
            mapped.append(("TTP-UNKNOWN", 0.3, "no heuristic rule hit"))

        for ttp, conf, why in mapped:
            out.append(
                {
                    "item": it.get("title", "Untitled")[:60],
                    "technique_id": ttp,
                    "confidence": conf,
                    "rationale": why,
                }
            )

    return out
