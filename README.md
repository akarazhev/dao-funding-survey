# What DAOs actually fund

A survey of **93 funding proposals across 29 governance forums**, collected in August 2026.

I kept running into the same question while looking at DAO work: what does a DAO actually pay an outside contributor for, and how much? The answers are public — they sit in governance forums — but nobody had put them side by side. So I did.

The dataset is in [`data/proposals.csv`](data/proposals.csv). Every row links to its source thread, so anything here can be checked.

---

## Method, and what it does not cover

Thirty-five forums were queried; 29 returned material. For each, recent topics were filtered on eleven terms — `service provider`, `contributor`, `compensation`, `engagement`, `retainer`, `budget request`, `grant`, `funding request`, `proposal to fund`, `mandate`, `stipend` — and the opening post of each match was read for amounts, periods and hours.

Four limits worth stating before any of the numbers are used:

- **This is a sample, not a census.** Only recent topics were scanned, so the data skews to 2026 — 71 of 93 proposals — and older programmes are underrepresented.
- **Amounts were extracted mechanically** and only 35 of 93 proposals yielded one. Where a proposal named several figures, the smallest plausible one was taken, on the assumption that it is closer to a line item than to a treasury total.
- **Keyword filtering misses things.** A proposal that never uses any of those eleven terms is invisible here.
- **A posted proposal is not a funded one.** Outcome was recorded only where the thread stated it.

## What gets funded, and for how much

| Category | Proposals | Amount range | Median |
|---|--:|---|--:|
| Engineering and tooling | 17 | $2,040 – $200,000 | $8,500 |
| Governance and operations | 16 | $1,800 – $329,000 | $3,500 |
| Data and monitoring | 9 | $2,000 – $10,000 | $5,000 |
| Risk and treasury | 9 | $5,000 – $110,000 | $39,000 |
| Growth and community | 9 | $600 – $30,000 | $30,000 |
| Security and audit | 4 | not stated in-thread | — |
| Other | 29 | $2,500 – $171,705 | $50,000 |

Two things stand out.

**Data and monitoring is the tightest and cheapest band in the set** — $2,000 to $10,000, and nothing above it. Every proposal in that category is a bounded piece of work: a monitoring module, a pipeline, a set of checks. None of them is a platform.

**Risk and treasury is bimodal**, which is why its median sits at $39,000 while its floor is $5,000. Small analytical pieces and large management mandates share a label but are not the same purchase. Which brings us to the vocabulary problem.

## "Treasury management" does not mean what an analyst assumes

In DAO usage it means running the money, not analysing it.

Compound's [Request for Proposals](https://www.comp.xyz/t/7867) sought professional managers for an initial **$20–25M allocation** of DAO reserves, with strategies spanning tokenised treasuries, conservative DeFi, liquidity provision and delta-neutral yield. Applicants included tokenisation platforms with hundreds of millions in TVL.

Gnosis DAO's [GIP-148](https://forum.gnosis.io/t/11957) is the same shape and instructive for a different reason. Its scope reads: operational treasury, **active asset management**, *risk and reporting infrastructure*, governance participation. Risk reporting is in there — but bundled into a mandate that also moves the money.

That bundling is the pattern. Across this sample there is no open call for risk analysis and reporting as a standalone service. It exists as a component of a manager's remit, alongside custody of the decision.

## Three kinds of open call

Everything found divides into three, and they buy different things.

**Treasury management RFPs** buy discretionary asset management. Large, few, and closed to anyone who cannot take responsibility for capital.

**Development grants** buy something built for the ecosystem — Optimism's Season 9 council, Celo's CICLOPS and Communities Guild, Superfluid's seasonal campaigns, Morpho's [MIP 93](https://forum.morpho.org/t/1177). Usually milestone-based, usually one-off.

**Service provider programmes** buy ongoing work from a named provider. [ENS SPP](https://discuss.ens.domains/t/22131) is the clearest example: seasonal, rubric-scored, with public calls where applicants can ask the committee how it weighs evidence. In the questions applicants ask there, one recurs — how heavily does a prior delivery record decide the outcome.

Of the three, only the last routinely buys a *service* rather than an asset manager or an artefact.

## Two cases worth putting side by side

These are the clearest illustration in the dataset that **channel and scope matter more than product readiness**.

**Quantir** is a three-person engineering team with a working DeFi risk monitoring platform — live collectors, transaction monitoring, normalised risk scoring, alert delivery, an explanation module, API and WebSocket interfaces, deployed across several protocols and chains. On 25 April 2026 they applied to two DAOs on the same day, unsolicited, outside any announced call:

- [CoW Protocol](https://forum.cow.fi/t/grant-application-quantir-risk-intelligence-layer-for-cow-protocol/3434) declined within two days: *"we have reviewed this internally and, at this time, we're not interested in moving forward."*
- [Balancer](https://forum.balancer.fi/t/grant-application-quantir-risk-monitoring-explainable-alerts-for-balancer-pools/7035) has not replied in nearly four months.

Nothing here reflects on the quality of their work — by the standard of "is it built", they were further along than most applicants in this dataset.

**MIP 93** points the other way. Morpho's grants pilot put up 200,000 MORPHO, invited public applications, and explicitly asked applicants to *pick a small initial scope and reapply in a later round*. It drew 119 submissions. Among the things it funded, per a contributor in a [later thread](https://forum.morpho.org/t/2246), was an institutional risk radar at **15,000 MORPHO, paid 20% up front, 20% on delivery, and the remainder against objective metrics**.

A risk tool, funded. The same category that was declined elsewhere.

The difference is not the product. It is that one arrived inside an announced call, at a deliberately small scope, with payment staged against delivery — and the other arrived unannounced, as a whole platform, asking to be evaluated on its merits.

## If you are trying to get funded

What the data suggests, stated as suggestions rather than rules:

**Find where applications are open** before deciding whom to write to. An open call resolves the cold-contact problem, the trust problem, and the problem of guessing who holds the budget, all at once.

**Ask for a small first scope.** Every funded example in the data-and-monitoring band is bounded work in the low single-digit thousands. Programmes say this outright when they bother to say anything.

**Offer staged payment.** Twenty percent up front and the rest against delivery costs a stranger nothing to accept, and it is the cheapest way to make a first engagement possible.

**Do not expect a built product to substitute for any of the above.** The clearest negative case in this dataset had the most finished product in it.

## Reproducing this

No dependencies beyond a Python 3 install. Discourse exposes `/latest.json` and
`/t/{id}.json` without authentication, which is the whole reason this is cheap to run.

```sh
python3 collect.py forums.txt   # -> raw.json
python3 analyse.py              # -> data/proposals.csv, prints the table above
```

`collect.py` reads the 35 forums in [`forums.txt`](forums.txt), scans two pages of
recent topics on each, keeps titles matching the eleven keywords, and reads the
opening post of the six newest matches per forum. It pauses half a second between
requests.

`analyse.py` assigns a category by keyword against title and body — first match
wins, so the order in the file is the priority order — and takes the smallest
figure between $500 and $500,000 as the amount, on the assumption that it is
closer to a line item than to the treasury it is drawn from.

Both choices are crude and both are visible in the code, which is the point: run
it against `raw.json` and you get [`data/proposals.csv`](data/proposals.csv) byte
for byte, so any disagreement is with a rule you can read rather than with a
number you have to trust.

Cells opening with `=`, `+`, `-` or `@` are prefixed with a quote before being
written. Titles are whatever someone typed into a forum, and a spreadsheet would
treat such a cell as a formula — a published dataset should not be able to do
anything to the person who opens it. No row in this sample needed it; the guard
is for the next run.

Re-running `collect.py` today will not reproduce this dataset. Forums move on,
and the sample is whatever was recent in August 2026. `raw.json` is committed so
the analysis stays checkable regardless.

## Data

[`data/proposals.csv`](data/proposals.csv) — 93 rows: forum, date, category, title, author, reply count, extracted amount, period, hours, and a link to the source thread.

[`raw.json`](raw.json) — what the collector saw, including a 300-character excerpt of each opening post. Categories are derived from these, so this is what to look at if a categorisation seems wrong.

Corrections are welcome. If a proposal is miscategorised, an amount is wrong, or an outcome is recorded that the thread does not support, the source link is right there and I would rather fix it than leave it.

---

*Andrey Karazhev · [minihub.app](https://minihub.app)*
