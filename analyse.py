#!/usr/bin/env python3
"""Turn raw.json into data/proposals.csv and print the summary table.

Categories are assigned by keyword against title and body, first match
wins, so the order below is the priority order. A proposal that matches
nothing lands in "other", which is a third of the set — the honest cost
of classifying by keyword rather than by reading.
"""
import csv, json, re
from collections import Counter, defaultdict

CATEGORIES = [
    ("risk-treasury",    r"\brisk\b|treasury|reserve|solvency|liquidat|collateral|depeg"),
    ("data-monitoring",  r"\bdata\b|analytic|dashboard|monitor|indexer|observab|oracle|metric"),
    ("security-audit",   r"security|audit|bug bount|pentest|formal verif"),
    ("engineering",      r"develop|engineer|build|sdk|integration|infra|tooling|node"),
    ("growth-community", r"growth|marketing|community|content|ambassador|event|hackathon"),
    ("governance-ops",   r"governance|operations|delegate|council|legal|master of coin|multisig"),
]

# Figures outside this range are almost never a contract price: below it
# they are version numbers and percentages, above it they are treasury
# totals quoted for context.
FLOOR, CEILING = 500, 500_000

# Titles come from forum posts, which anyone can write. A spreadsheet treats a
# cell opening with any of these as a formula, so a topic called "=HYPERLINK(..)"
# would execute for whoever opens the published CSV. Prefixing a quote makes the
# cell inert and still readable.
FORMULA_LEAD = ("=", "+", "-", "@", "\t", "\r")


def defuse(value):
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(FORMULA_LEAD) else text


def categorise(row):
    text = f"{row['title']} {row['body']}"
    for name, pattern in CATEGORIES:
        if re.search(pattern, text, re.I):
            return name
    return "other"


def plausible(row):
    """Every figure in the post that falls inside the plausible range, sorted.

    The published amount is the smallest of these, on the assumption that it
    is closer to a line item than to the treasury it is drawn from. That
    assumption is a guess, and on most rows carrying more than one figure it
    is the guess - not the source - that decides the number. So the largest
    is written out beside it and the count of candidates with them: a reader
    can see at a glance which rows the rule actually chose for, and what the
    other choice would have been.
    """
    values = []
    for raw in row["amounts"]:
        m = re.match(r"([\d.]+)\s*(k|m|million)?", raw.strip().lstrip("$").replace(",", ""), re.I)
        if not m:
            continue
        value = float(m.group(1))
        suffix = (m.group(2) or "").lower()
        value *= 1_000 if suffix == "k" else 1_000_000 if suffix in ("m", "million") else 1
        if FLOOR <= value <= CEILING:
            values.append(value)
    return sorted(values)


def main():
    rows = json.load(open("raw.json"))
    counts = Counter()
    lows, highs = defaultdict(list), defaultdict(list)
    decided_by_rule = 0

    with open("data/proposals.csv", "w", newline="") as f:
        # Explicit LF. The csv module defaults to CRLF, git rewrites it to LF on
        # commit, and the file a cloner regenerates then differs from the file in
        # the repository - which would make the byte-for-byte claim below false
        # for everyone except the author.
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["forum", "date", "category", "title", "author",
                    "replies", "amount_usd_low", "amount_usd_high",
                    "amounts_found", "period", "hours", "url"])
        for row in sorted(rows, key=lambda r: (r["forum"], r["date"])):
            category, values = categorise(row), plausible(row)
            counts[category] += 1
            if values:
                lows[category].append(values[0])
                highs[category].append(values[-1])
                if values[0] != values[-1]:
                    decided_by_rule += 1
            w.writerow([defuse(c) for c in (
                row["forum"], row["date"], category, row["title"], row["author"],
                row["replies"],
                int(values[0]) if values else "",
                int(values[-1]) if values else "",
                len(values) or "",
                row["period"] or "", row["hours"] or "", row["url"])])

    # Both ranges are printed because the difference between them is the size
    # of the guess. A band quoted from the left column alone reads as measured
    # when part of it was chosen.
    print(f"{'category':<18}{'n':>4}{'amt':>5}"
          f"{'range, lowest taken':>26}{'median':>10}{'range, highest taken':>26}")
    for category, n in counts.most_common():
        low, high = sorted(lows[category]), sorted(highs[category])
        if low:
            span_l = f"${low[0]:,.0f} - ${low[-1]:,.0f}"
            span_h = f"${high[0]:,.0f} - ${high[-1]:,.0f}"
            print(f"{category:<18}{n:>4}{len(low):>5}{span_l:>26}"
                  f"{low[len(low)//2]:>9,.0f}{span_h:>26}")
        else:
            print(f"{category:<18}{n:>4}{0:>5}{'not stated':>26}{'':>10}{'':>26}")
    with_amount = sum(len(v) for v in lows.values())
    print(f"\n{sum(counts.values())} proposals, {with_amount} with an extractable "
          f"amount, of which {decided_by_rule} carried more than one candidate - "
          f"there the smallest-figure rule, not the thread, set the number.")


if __name__ == "__main__":
    main()
