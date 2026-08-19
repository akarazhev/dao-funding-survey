#!/usr/bin/env python3
"""Collect funding-related proposals from Discourse governance forums.

Reads forum hostnames from forums.txt, one per line, and writes raw
records to raw.json. Standard library only.

Every Discourse instance exposes /latest.json and /t/{id}.json without
authentication, which is the whole reason this survey is cheap to run.
"""
import json, re, sys, time, urllib.request, urllib.error

# A proposal is a candidate if its title contains any of these. This is the
# survey's coarsest instrument: anything phrased without them is invisible.
KEYWORDS = re.compile(
    r"service provider|contributor|compensation|engagement|retainer"
    r"|budget request|grant|funding request|proposal to fund|mandate|stipend",
    re.I,
)
MONEY = re.compile(
    r"\$\s?([\d][\d,.]{2,})(?:\s?(k|m|million))?"
    r"|\b([\d][\d,.]{3,})\s?(USDC|USDT|DAI|USD)\b",
    re.I,
)
HOURS = re.compile(r"(\d{1,3})\s*hours?\s*(?:per|a|/)\s*(week|month)", re.I)
PERIOD = re.compile(
    r"\b(per month|monthly|per year|annual|/mo|/month"
    r"|6 months|twelve months|12 months|quarterly)\b", re.I,
)
TAGS = re.compile(r"<[^>]+>")

PER_FORUM = 6      # topics read per forum, newest first
PAGES = 2          # pages of /latest.json to scan
PAUSE = 0.5        # seconds between requests, to stay a polite visitor


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dao-funding-survey/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}


def plain(html):
    return re.sub(r"\s+", " ", TAGS.sub(" ", html or "")).strip()


def collect(forum):
    topics = []
    for page in range(PAGES):
        data = fetch(f"https://{forum}/latest.json?order=created&page={page}")
        topics += data.get("topic_list", {}).get("topics", [])
        time.sleep(PAUSE)

    candidates = sorted(
        (t for t in topics if KEYWORDS.search(t.get("title", ""))),
        key=lambda t: t.get("created_at", ""),
        reverse=True,
    )[:PER_FORUM]

    out = []
    for topic in candidates:
        full = fetch(f"https://{forum}/t/{topic['id']}.json")
        time.sleep(PAUSE)
        posts = full.get("post_stream", {}).get("posts", [])
        if not posts:
            continue
        body = plain(posts[0].get("cooked"))
        hours, period = HOURS.search(body), PERIOD.search(body)
        out.append({
            "forum": forum,
            "date": (full.get("created_at") or "")[:10],
            "title": full.get("title"),
            "author": posts[0].get("username"),
            "replies": full.get("posts_count"),
            "amounts": [m.group(0) for m in MONEY.finditer(body)][:4],
            "hours": hours.group(0) if hours else None,
            "period": period.group(0) if period else None,
            "url": f"https://{forum}/t/{full.get('slug')}/{topic['id']}",
            "body": body[:300],
        })
    return out


def main():
    forums = [
        line.strip()
        for line in open(sys.argv[1] if len(sys.argv) > 1 else "forums.txt")
        if line.strip() and not line.startswith("#")
    ]
    rows = []
    for forum in forums:
        found = collect(forum)
        rows += found
        print(f"{forum}: {len(found)}", flush=True)
    json.dump(rows, open("raw.json", "w"), ensure_ascii=False, indent=1)
    print(f"\n{len(rows)} proposals from {len(set(r['forum'] for r in rows))} forums -> raw.json")


if __name__ == "__main__":
    main()
