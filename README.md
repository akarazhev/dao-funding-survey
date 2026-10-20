# What DAOs actually fund

A survey of 93 funding proposals across 29 governance forums, collected in August 2026.

I kept running into the same question while looking at DAO work: what does a DAO actually pay an outside
contributor for, and how much? The answers are public, in governance forums, but nobody had put them side by
side. So I did.

The dataset is in [`data/proposals.csv`](data/proposals.csv). Every row links to its source thread.

## Method and limits

I queried 35 forums, and 29 returned material. On each, recent topics were filtered on eleven terms
(`service provider`, `contributor`, `compensation`, `engagement`, `retainer`, `budget request`, `grant`,
`funding request`, `proposal to fund`, `mandate`, `stipend`), and the opening post of each match was read for
amounts, periods and hours.

What to keep in mind before using the numbers:

- It is a sample, not a census. Only recent topics were scanned, so 71 of the 93 proposals are from 2026.
- Amounts were extracted mechanically, and only 35 of 93 proposals gave one. Where a proposal named several
  figures, I took the smallest plausible one, assuming it is closer to a line item than to a treasury total.
  That rule matters: 21 of the 35 named more than one figure. The largest candidate is published next to it in
  `amount_usd_high`, so you can see the effect row by row.
- A proposal that never uses any of the eleven terms is invisible here.
- A posted proposal is not a funded one. The outcome was recorded only where the thread stated it.

## What gets funded, and for how much

| Category | Proposals | With an amount | Range, smallest taken | Median | Range, largest taken |
|---|--:|--:|---|--:|---|
| Engineering and tooling | 17 | 5 | $2,040 – $200,000 | $8,500 | $5,890 – $200,000 |
| Governance and operations | 16 | 8 | $1,800 – $329,000 | $3,500 | $3,000 – $329,000 |
| Data and monitoring | 9 | 4 | $2,000 – $10,000 | $5,000 | $10,000 – $15,000 |
| Risk and treasury | 9 | 5 | $5,000 – $110,000 | $39,000 | $5,000 – $279,274 |
| Growth and community | 9 | 2 | $600 – $30,000 | $30,000 | $1,200 – $50,000 |
| Security and audit | 4 | 0 | not stated in-thread | | |
| Other | 29 | 11 | $2,500 – $171,705 | $50,000 | $5,000 – $356,996 |

Look at the "With an amount" column first: each range rests on a handful of rows. Where the last column is far
from the fourth, the band depends on the extraction rule as much as on the forums.

**Data and monitoring** comes out cheapest, $2,000 to $10,000, but that is thin. Four of its nine proposals state
a figure, all four named several, and read the other way the band is $10,000 to $15,000. What holds either way
is the shape of the work: every proposal in the category is a bounded piece (a monitoring module, a pipeline,
a set of checks), and none is a platform.

**Risk and treasury** has two kinds of proposal under one label, small analytical pieces and large management
mandates, which is why the median is $39,000 while the floor is $5,000.

## "Treasury management" means running the money

In DAO usage it means managing the reserves, not analysing them.

Compound's [Request for Proposals](https://www.comp.xyz/t/7867) sought professional managers for an initial
**$20–25M allocation** of DAO reserves, across tokenised treasuries, conservative DeFi, liquidity provision and
delta-neutral yield. Applicants included tokenisation platforms with hundreds of millions in TVL.

Gnosis DAO's [GIP-148](https://forum.gnosis.io/t/11957) has the same shape: operational treasury, active asset
management, risk and reporting infrastructure, governance participation. Risk reporting is there, but bundled
into a mandate that also moves the money. In this sample I found no open call for risk analysis and reporting
as a standalone service.

## Three kinds of open call

- **Treasury management RFPs** buy discretionary asset management. They are large, few, and closed to anyone
  who cannot take responsibility for capital.
- **Development grants** buy something built for the ecosystem: Optimism's Season 9 council, Celo's CICLOPS and
  Communities Guild, Superfluid's seasonal campaigns, Morpho's [MIP 93](https://forum.morpho.org/t/1177).
  Usually milestone-based and one-off.
- **Service provider programmes** buy ongoing work from a named provider. [ENS SPP](https://discuss.ens.domains/t/22131)
  is the clearest example: seasonal, scored against a rubric, with public calls where applicants can ask the
  committee questions. One question keeps coming up there: how much a prior delivery record decides the outcome.

Only the last of the three routinely buys a service rather than an asset manager or an artefact.

## Two cases side by side

**Quantir** is a three-person team with a working DeFi risk monitoring platform: live collectors, transaction
monitoring, risk scoring, alerts with explanations, API and WebSocket access, deployed across several protocols
and chains. On 25 April 2026 they applied to two DAOs on the same day, outside any announced call:

- [CoW Protocol](https://forum.cow.fi/t/grant-application-quantir-risk-intelligence-layer-for-cow-protocol/3434)
  declined within two days: *"we have reviewed this internally and, at this time, we're not interested in moving
  forward."*
- [Balancer](https://forum.balancer.fi/t/grant-application-quantir-risk-monitoring-explainable-alerts-for-balancer-pools/7035)
  had not replied after nearly four months.

That says nothing about the quality of their work; their product was further along than most in this dataset.

**MIP 93** went the other way. Morpho's grants pilot put up 200,000 MORPHO, invited public applications and asked
applicants to pick a small initial scope and reapply in a later round. It drew 119 submissions. Among the things
it funded, according to a contributor in a [later thread](https://forum.morpho.org/t/2246), was an institutional
risk radar at **15,000 MORPHO, paid 20% up front, 20% on delivery and the rest against objective metrics**.

So a risk tool did get funded. It came inside an announced call, at a small scope, with payment staged against
delivery. The declined one came unannounced, as a whole platform.

## If you are trying to get funded

These are suggestions from the data, not rules:

- **Look for open calls first.** They answer the questions of whom to write to, whether you will be trusted and
  who holds the budget.
- **Ask for a small first scope.** Every funded example in data and monitoring is bounded work, priced between a
  few thousand and fifteen thousand dollars, depending on how the figures are read.
- **Offer staged payment.** Twenty percent up front and the rest on delivery is easy for a stranger to accept.
- **A finished product doesn't replace any of this.** The clearest refusal here had the most finished product.

## Reproducing this

Python 3 only. Discourse serves `/latest.json` and `/t/{id}.json` without authentication.

```sh
python3 collect.py forums.txt   # -> raw.json
python3 analyse.py              # -> data/proposals.csv, prints the table above
```

`collect.py` reads the 35 forums in [`forums.txt`](forums.txt), scans two pages of recent topics, keeps titles
that match the eleven terms and reads the opening post of the six newest matches per forum. `analyse.py` picks
a category by the first matching keyword and takes the smallest figure between $500 and $500,000, writing the
largest candidate and the number of candidates next to it. Running it on the committed `raw.json` reproduces
`data/proposals.csv` byte for byte. Running `collect.py` today won't reproduce the dataset, because forums move
on.

## Data

- [`data/proposals.csv`](data/proposals.csv): 93 rows with forum, date, category, title, author, reply count, the
  smallest and largest plausible amounts with the number of candidates, period, hours and a link to the thread.
- [`raw.json`](raw.json): what the collector saw, with a 300-character excerpt of each opening post.

If a proposal is in the wrong category, an amount is wrong, or an outcome isn't supported by its thread, tell me
and I'll fix it.

---

*Andrey Karazhev · [minihub.app](https://minihub.app)*
