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


def amount(row):
    """Smallest plausible figure in the post, on the assumption that it is
    closer to a line item than to the treasury it is drawn from."""
    best = None
    for raw in row["amounts"]:
        m = re.match(r"([\d.]+)\s*(k|m|million)?", raw.strip().lstrip("$").replace(",", ""), re.I)
        if not m:
            continue
        value = float(m.group(1))
        suffix = (m.group(2) or "").lower()
        value *= 1_000 if suffix == "k" else 1_000_000 if suffix in ("m", "million") else 1
        if FLOOR <= value <= CEILING and (best is None or value < best):
            best = value
    return best


def main():
    rows = json.load(open("raw.json"))
    counts, amounts = Counter(), defaultdict(list)

    with open("data/proposals.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["forum", "date", "category", "title", "author",
                    "replies", "amount_usd_low", "period", "hours", "url"])
        for row in sorted(rows, key=lambda r: (r["forum"], r["date"])):
            category, value = categorise(row), amount(row)
            counts[category] += 1
            if value:
                amounts[category].append(value)
            w.writerow([defuse(c) for c in (
                row["forum"], row["date"], category, row["title"], row["author"],
                row["replies"], int(value) if value else "",
                row["period"] or "", row["hours"] or "", row["url"])])

    print(f"{'category':<18}{'n':>4}{'range':>26}{'median':>12}")
    for category, n in counts.most_common():
        values = sorted(amounts[category])
        if values:
            span = f"${min(values):,.0f} - ${max(values):,.0f}"
            print(f"{category:<18}{n:>4}{span:>26}{values[len(values)//2]:>11,.0f}")
        else:
            print(f"{category:<18}{n:>4}{'not stated':>26}{'':>12}")
    print(f"\n{sum(counts.values())} proposals, "
          f"{sum(len(v) for v in amounts.values())} with an extractable amount")


if __name__ == "__main__":
    main()
