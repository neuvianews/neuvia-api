# Neuvia API

**Narrative intelligence for news.** Neuvia tracks how news coverage portrays people, companies and places, storyline by storyline and day by day, and measures each news channel against a balanced reference built from publishers across outlet types.

[Get a free key](https://neuvianews.com/dashboard?plan=free&ref=gh-readme) · [API reference](https://neuvianews.com/docs?ref=gh-readme) · [How the reference works](https://neuvianews.com/blog/narrative-intelligence?ref=gh-readme) · [Explorer](https://neuvianews.com/explorer?ref=gh-readme) · [OpenAPI spec](openapi.yaml)

## Two building blocks

1. **Storyline time series.** Every article is broken into entity-concept pairs, or storylines, such as `federal reserve` + `rate hike`. Each pair gets a score from -1 to 1 for how the article portrays the entity, and the scores roll up by day for each channel: Google News, the financial press, and local outlets in all 50 US states.
2. **A balanced reference.** For the same storylines, Balanced Discoverable Media Sentiment (BDMS) is built from discoverable coverage across wire, broadcast, print, independent and local outlets. Each reference comes with a 95% confidence interval.

Put them together and you get **Channel Narrative Divergence (CND)**: how far a channel's coverage sits from the reference, day by day.

## Quickstart

[Get a free key](https://neuvianews.com/dashboard?plan=free&ref=gh-readme) with just an email: 1,000 calls a month and 7 days of history, no card. Then:

```bash
export NEUVIA_KEY=nv_your_key

# 1. Find the entity's canonical name
curl -H "Authorization: Bearer $NEUVIA_KEY" \
  "https://neuvianews.com/api/v1/search?q=federal"

# 2. List its storylines this week, each with its BDMS reference
curl -H "Authorization: Bearer $NEUVIA_KEY" \
  "https://neuvianews.com/api/v1/entity/federal%20reserve/coverage?days=7"

# 3. Pull the daily series for one storyline
curl -H "Authorization: Bearer $NEUVIA_KEY" \
  "https://neuvianews.com/api/v1/narratives?entity=federal%20reserve&concept=rate%20hike"
```

Step 3 returns one row per day (trimmed here to two):

```json
{
  "entity": "federal reserve",
  "concept": "rate hike",
  "channel": "all",
  "series": [
    { "date": "2026-11-10", "mentions": 6, "sentiment": 0, "bdms": 0.26, "bdmsCiLow": 0.198, "bdmsCiHigh": 0.323, "bdmsSampleSize": 15, "bdmsComputedAt": "2026-11-09", "cnd": -0.26 },
    { "date": "2026-11-11", "mentions": 7, "sentiment": -0.3, "bdms": 0.26, "bdmsCiLow": 0.198, "bdmsCiHigh": 0.323, "bdmsSampleSize": 15, "bdmsComputedAt": "2026-11-09", "cnd": -0.56 }
  ]
}
```

On November 11, seven articles across our channels scored the Federal Reserve's rate-hike storyline at -0.30 on average. The balanced reference stood at +0.26 (95% CI +0.20 to +0.32), so the day's coverage ran 0.56 below it.

## Python

```python
import os
import requests

API = "https://neuvianews.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['NEUVIA_KEY']}"}

r = requests.get(f"{API}/narratives", headers=HEADERS, timeout=30,
                 params={"entity": "federal reserve", "concept": "rate hike"})
r.raise_for_status()
for day in r.json()["series"]:
    print(day["date"], day["mentions"], day["sentiment"], day["bdms"], day["cnd"])
```

[examples/quickstart.py](examples/quickstart.py) runs the whole flow above for any entity: `python examples/quickstart.py "nvidia"`.

## Endpoints

The base URL is `https://neuvianews.com/api`. Pass your key as `Authorization: Bearer <key>` or `?api_key=<key>`.

| Endpoint | Returns | Plan |
|---|---|---|
| `GET /v1/search` | Canonical entity names matching a query | Free |
| `GET /v1/trending` | Entities with the most coverage in the last 7 days | Free |
| `GET /v1/entity/{entity}/coverage` | An entity's storylines, with mentions, average score and BDMS | Free |
| `GET /v1/narratives` | Daily series for one storyline: mentions, score, BDMS with its CI, and CND | Free |
| `GET /v1/articles` | The articles behind a storyline, an entity or a keyword | Free (keyword search on its own from Starter) |
| `GET /v1/stocks/sentiment` | Financial press scores for the most-covered stocks, with market context | Starter |
| `GET /v1/local/{state}` | The latest local coverage in any US state | Professional |
| `POST /v1/analyze` | Storylines, scores and BDMS for article text you send | Professional |

`/v1/narratives` and `/v1/articles` take a `channel` (`google-news`, `financial`, `local` or `all`) and a date window (`from`, `to` or `days`).

The full contract, with real example responses, is in [openapi.yaml](openapi.yaml). Import it into Postman or Insomnia, or generate a client from it. The [API reference](https://neuvianews.com/docs?ref=gh-readme) covers the same ground for humans.

## Plans

| | Free | Starter | Professional | Enterprise |
|---|---|---|---|---|
| Price | $0 | $49/month | $199/month | Custom |
| Calls per month | 1,000 | 20,000 | 200,000 | Unlimited |
| History | 7 days | 90 days | Since March 2026 | Since March 2026 |

Every response carries `X-RateLimit-Limit`, `X-RateLimit-Used` and `X-Plan` headers. [Compare plans](https://neuvianews.com/?ref=gh-readme#pricing).

## How the reference works

BDMS samples discoverable coverage of each storyline across outlet types (wire, broadcast, print, independent and local), alternating between left-, center- and right-leaning publishers. Scores are averaged within each publisher, then across publishers within each outlet type, then equally across types, so no single outlet or format dominates. The confidence interval comes from resampling publishers. The [write-up](https://neuvianews.com/blog/narrative-intelligence?ref=gh-readme) walks through the method with two worked examples.

## Citing and contact

If you publish work based on Neuvia data, please credit Neuvia (neuvianews.com). Questions or custom plans: api@delvedx.com.

The code and the OpenAPI spec in this repository are MIT-licensed. Neuvia is a product of DelveDx.
