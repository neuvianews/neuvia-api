"""Neuvia API quickstart: find an entity, list its storylines, then pull one storyline's daily series.

Runs on a free key (https://neuvianews.com/dashboard?plan=free&ref=gh-quickstart):

    pip install requests
    export NEUVIA_KEY=nv_your_key
    python quickstart.py "federal reserve"
"""
import os
import sys
from urllib.parse import quote

import requests

API = "https://neuvianews.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['NEUVIA_KEY']}"}


def get(path, **params):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=30)
    if not r.ok:
        sys.exit(f"{r.status_code}: {r.json().get('error', r.text)}")
    return r.json()


def fmt(x):
    return "-" if x is None else f"{x:+.2f}"


query = sys.argv[1] if len(sys.argv) > 1 else "federal reserve"

# 1. Resolve the canonical entity name (lowercase, full name)
matches = get("/search", q=query, limit=1)["results"]
if not matches:
    sys.exit(f"No entity matching {query!r} in the last 30 days")
entity = matches[0]["entity"]

# 2. Its storylines over the last 7 days, each with its BDMS reference
coverage = get(f"/entity/{quote(entity, safe='')}/coverage", days=7)["coverage"]
print(f"Storylines for {entity!r}, last 7 days\n")
print(f"{'concept':<34} {'mentions':>8} {'score':>6} {'BDMS':>6}  95% CI")
for c in coverage[:10]:
    ci = f"{fmt(c['bdmsCiLow'])} to {fmt(c['bdmsCiHigh'])}" if c["bdms"] is not None else ""
    print(f"{c['concept'][:34]:<34} {c['mentions']:>8} {fmt(c['avgSentiment']):>6} {fmt(c['bdms']):>6}  {ci}")

# 3. The daily series for the most-mentioned storyline that has a reference
top = next((c for c in coverage if c["bdms"] is not None), None)
if top is None:
    sys.exit("\nNone of these storylines has a BDMS reference yet.")
series = get("/narratives", entity=entity, concept=top["concept"])["series"]
print(f"\nDaily series for {entity!r} + {top['concept']!r} (CND = score - BDMS)\n")
print(f"{'date':<11} {'mentions':>8} {'score':>6} {'BDMS':>6} {'CND':>6}")
for d in series:
    print(f"{d['date']:<11} {d['mentions']:>8} {fmt(d['sentiment']):>6} {fmt(d['bdms']):>6} {fmt(d['cnd']):>6}")
