from dotenv import load_dotenv
load_dotenv()  # ← load .env when this file is imported

import json, os, re, datetime
from dateutil import parser
import requests
import feedparser
from html.parser import HTMLParser



class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []

    def handle_data(self, data):
        self.texts.append(data)

    def get_data(self):
        return " ".join(self.texts).strip()


def clean_html(text: str) -> str:
    s = MLStripper()
    s.feed(text or "")
    return s.get_data()


def _to_iso8601(dt):
    if isinstance(dt, str):
        try:
            return parser.parse(dt).isoformat()
        except Exception:
            return dt
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)


def normalize(item: dict) -> dict:
    return {
        "id": item.get("id") or item.get("url") or item.get("title"),
        "source": item.get("source", "UNKNOWN"),
        "published_at": _to_iso8601(
            item.get("published_at", datetime.datetime.utcnow().isoformat())
        ),
        "title": clean_html(item.get("title", "")),
        "summary": clean_html(item.get("summary", "")),
        "cve_list": item.get("cve_list", []),
        "cvss_max": float(item.get("cvss_max", 0.0)),
        "iocs": item.get(
            "iocs",
            {
                "ips": [],
                "domains": [],
                "urls": [],
            },
        ),
        "products": item.get("products", []),
        "mitre_ttps": item.get("mitre_ttps", []),
        # geo_hints is optionally set by collectors; enrich_all() may extend it
        "geo_hints": item.get("geo_hints", []),
    }


def normalize_all(items):
    return [normalize(x) for x in items]


def enrich_all(items):
    """Very light geo hinting based on keywords in title/summary.
    If a collector already set geo_hints, we extend that list instead of replacing it.
    """
    GEO_KEYWORDS = [
        ("USA", "US"),
        ("United States", "US"),
        ("Saudi Arabia", "SA"),
        ("Saudi", "SA"),
        ("KSA", "SA"),
        ("United Arab Emirates", "AE"),
        ("UAE", "AE"),
        ("United Kingdom", "GB"),
        ("UK", "GB"),
        ("China", "CN"),
        ("Russia", "RU"),
        ("Europe", "EU"),
    ]

    for it in items:
        text = f"{it.get('title','')} {it.get('summary','')}"
        lower = text.lower()
        geos = set(it.get("geo_hints", []))
        for kw, iso in GEO_KEYWORDS:
            if kw.lower() in lower:
                geos.add(iso)
        it["geo_hints"] = sorted(geos)
    return items


# =========================
#  NVD CVE FEED
# =========================

def fetch_nvd_cves(limit: int = 5):
    """Fetch recent CVEs from NVD REST API and map into the common item schema."""
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage={limit}"
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        return []

    if response.status_code != 200:
        return []

    data = response.json()
    items = []

    for v in data.get("vulnerabilities", []):
        cve = v.get("cve", {})
        cve_id = cve.get("id") or cve.get("CVE", {}).get("ID")
        if not cve_id:
            continue

        description = ""
        descs = cve.get("descriptions") or []
        if descs:
            description = descs[0].get("value", "")

        cvss = 0.0
        metrics = cve.get("metrics", {})
        if "cvssMetricV31" in metrics:
            cvss = metrics["cvssMetricV31"][0].get("cvssData", {}).get(
                "baseScore", 0.0
            )
        elif "cvssMetricV3" in metrics:
            cvss = metrics["cvssMetricV3"][0].get("cvssData", {}).get(
                "baseScore", 0.0
            )

        items.append(
            {
                "id": cve_id,
                "source": "NVD",
                "published_at": cve.get(
                    "published", datetime.datetime.utcnow().isoformat()
                ),
                "title": cve_id,
                "summary": description,
                "cve_list": [cve_id],
                "cvss_max": cvss,
                "iocs": {"ips": [], "domains": [], "urls": []},
                "products": [],
                "mitre_ttps": [],
            }
        )

    return items


# =========================
#  CISA ADVISORIES
# =========================

def fetch_cisa_advisories(limit: int = 5):
    """Fetch recent CISA advisories via the public XML feed."""
    url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:limit]:
        items.append(
            {
                "id": entry.get("id") or entry.get("link"),
                "source": "CISA",
                "published_at": entry.get(
                    "published", datetime.datetime.utcnow().isoformat()
                ),
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "cve_list": [],
                "cvss_max": 0.0,
                "iocs": {"ips": [], "domains": [], "urls": []},
                "products": [],
                "mitre_ttps": [],
            }
        )

    return items


# =========================
#  CISCO TALOS VENDOR FEED
# =========================

def fetch_cisco_talos(limit: int = 5):
    """Fetch recent posts from Cisco Talos Intelligence blog RSS feed."""
    url = "http://feeds.feedburner.com/feedburner/Talos"
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:limit]:
        items.append(
            {
                "id": entry.get("id") or entry.get("link"),
                "source": "Cisco Talos",
                "published_at": entry.get(
                    "published", datetime.datetime.utcnow().isoformat()
                ),
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "cve_list": [],
                "cvss_max": 0.0,
                "iocs": {"ips": [], "domains": [], "urls": []},
                "products": [],
                "mitre_ttps": [],
            }
        )

    return items


# =========================
#  MICROSOFT MSRC VENDOR FEED
# =========================

def fetch_msrc(limit: int = 5):
    """Fetch recent Microsoft Security Update Guide entries via RSS."""
    url = "https://msrc.microsoft.com/update-guide/rss"
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        cves = re.findall(r"CVE-\d{4}-\d+", title)
        items.append(
            {
                "id": entry.get("id") or entry.get("link"),
                "source": "MSRC",
                "published_at": entry.get(
                    "published", datetime.datetime.utcnow().isoformat()
                ),
                "title": title,
                "summary": entry.get("summary", ""),
                "cve_list": cves,
                "cvss_max": 0.0,
                "iocs": {"ips": [], "domains": [], "urls": []},
                "products": [],
                "mitre_ttps": [],
            }
        )

    return items


# =========================
#  MITRE ATT&CK JSON (TTPs)
# =========================

def fetch_mitre_attack(limit: int = 20):
    """Load MITRE ATT&CK Enterprise techniques from the official STIX JSON."""
    url = (
        "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/"
        "enterprise-attack/enterprise-attack.json"
    )
    try:
        response = requests.get(url, timeout=20)
    except Exception:
        return []

    if response.status_code != 200:
        return []

    data = response.json()
    objects = data.get("objects", [])
    items = []

    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue

        external_id = None
        for ref in obj.get("external_references", []):
            ext_id = ref.get("external_id")
            if ext_id and ext_id.startswith("T"):
                external_id = ext_id
                break

        if not external_id:
            continue

        items.append(
            {
                "id": obj.get("id"),
                "source": "MITRE ATT&CK",
                "published_at": obj.get(
                    "modified",
                    obj.get("created", datetime.datetime.utcnow().isoformat()),
                ),
                "title": obj.get("name", ""),
                "summary": obj.get("description", ""),
                "cve_list": [],
                "cvss_max": 0.0,
                "iocs": {"ips": [], "domains": [], "urls": []},
                "products": [],
                "mitre_ttps": [external_id],
            }
        )

        if len(items) >= limit:
            break

    return items


# =========================
#  ThreatFox IOCs (Abuse.ch)
# =========================

def fetch_threatfox_iocs(limit: int = 50, days: int = 1):
    """Fetch recent Indicators of Compromise from ThreatFox.

    Requires an Auth-Key from abuse.ch in the THREATFOX_AUTH_KEY env var.
    We only map network IOCs which make sense for a geo map (IP, domain, URL).
    """
    auth_key = os.environ.get("THREATFOX_AUTH_KEY")
    if not auth_key:
        # No API key configured → skip gracefully
        return []

    url = "https://threatfox-api.abuse.ch/api/v1/"
    headers = {"Auth-Key": auth_key}
    payload = {"query": "get_iocs", "days": max(1, min(days, 7))}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
    except Exception:
        return []

    if resp.status_code != 200:
        return []

    data = resp.json()
    if data.get("query_status") != "ok":
        return []

    items = []
    for row in data.get("data", [])[:limit]:
        indicator = row.get("ioc")
        ioc_type = (row.get("ioc_type") or "").lower()
        if not indicator or not ioc_type:
            continue

        iocs = {"ips": [], "domains": [], "urls": []}
        if ioc_type.startswith("ip"):
            iocs["ips"].append(indicator)
        elif ioc_type in ("domain", "hostname", "fqdn"):
            iocs["domains"].append(indicator)
        elif ioc_type == "url":
            iocs["urls"].append(indicator)
        else:
            # skip hashes etc. for the geo/IoC map
            continue

        country = row.get("country")
        geo_hints = []
        if country:
            geo_hints = [country.upper()]

        items.append(
            {
                "id": str(row.get("id") or indicator),
                "source": "ThreatFox",
                "published_at": row.get(
                    "first_seen", datetime.datetime.utcnow().isoformat()
                ),
                "title": indicator,
                "summary": row.get("threat_type_desc") or row.get("threat_type") or "",
                "cve_list": [],
                "cvss_max": 0.0,
                "iocs": iocs,
                "products": [],
                "mitre_ttps": [],
                "geo_hints": geo_hints,
            }
        )

    return items


# =========================
#  Aggregator
# =========================

def collect_all_sources():
    """Aggregate all live sources into a single list.

    Includes:
      - NVD CVEs
      - CISA advisories
      - Cisco Talos Intelligence
      - Microsoft MSRC
      - MITRE ATT&CK techniques
      - ThreatFox IOCs (network indicators with geo)
    """
    nvd_items = fetch_nvd_cves(limit=5)
    cisa_items = fetch_cisa_advisories(limit=5)
    talos_items = fetch_cisco_talos(limit=5)
    msrc_items = fetch_msrc(limit=5)
    mitre_items = fetch_mitre_attack(limit=20)
    threatfox_items = fetch_threatfox_iocs(limit=50, days=1)

    all_items = (
        nvd_items
        + cisa_items
        + talos_items
        + msrc_items
        + mitre_items
        + threatfox_items
    )

    return all_items
