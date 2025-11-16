from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import feeds

app = FastAPI(
    title="Threat Intel API",
    description="Backend API for animated cyber threat map",
)

# Allow your React dev server (http://localhost:3000) to call this API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/iocs")
def get_iocs(limit: int = 50, days: int = 1):
    """
    Returns normalized IoCs + geo hints from ThreatFox.
    This reuses your existing core.feeds logic.
    """
    raw = feeds.fetch_threatfox_iocs(limit=limit, days=days)
    items = [feeds.normalize(it) for it in raw]

    payload = []
    for it in items:
        iocs = it.get("iocs") or {}
        payload.append(
            {
                "title": it.get("title", ""),
                "source": it.get("source", "ThreatFox"),
                "geo_hints": it.get("geo_hints", []),
                "iocs": {
                    "ips": iocs.get("ips", []),
                    "domains": iocs.get("domains", []),
                    "urls": iocs.get("urls", []),
                },
            }
        )

    return {"items": payload}


@app.get("/health")
def health():
    return {"status": "ok"}
