from collections import defaultdict
from datetime import datetime, timezone
import math

def _days_since(dt_iso):
    try:
        dt = datetime.fromisoformat(dt_iso.replace('Z','+00:00'))
    except:
        return 999
    delta = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
    return max(delta.days + delta.seconds/86400, 0.0)

def _recency_decay(days, half_life=7.0):
    return math.exp(-math.log(2) * days/half_life)

def _duplication_score(items):
    # group by normalized title key
    buckets = defaultdict(list)
    for it in items:
        key = (it['title'][:50].lower()).strip()
        buckets[key].append(it)
    dup_score = {it['id']: (len(buckets[(it['title'][:50].lower()).strip()]) - 1) / 4.0
                 for it in items}
    # cap at 1
    return {k: min(1.0, v) for k, v in dup_score.items()}

def score_and_group(items):
    dup = _duplication_score(items)
    for it in items:
        cvss = min(max(float(it.get('cvss_max', 0.0)), 0.0), 10.0) / 10.0
        recency = _recency_decay(_days_since(it.get('published_at','')))
        source = it.get('source','UNKNOWN')
        source_w = 1.0 if source in ('CISA','CERT','NVD') else 0.7
        ioc_density = 0.0
        iocs = it.get('iocs', {})
        if iocs:
            ioc_density = min(1.0, (len(iocs.get('ips',[])) + len(iocs.get('domains',[])) + len(iocs.get('urls',[]))) / 5.0)
        score = 0.35*cvss + 0.25*dup.get(it['id'],0.0) + 0.15*source_w + 0.15*recency + 0.10*ioc_density
        it['rank_score'] = round(score, 4)
    return sorted(items, key=lambda x: x['rank_score'], reverse=True)

def select_top(items, k=5):
    return items[:k]
