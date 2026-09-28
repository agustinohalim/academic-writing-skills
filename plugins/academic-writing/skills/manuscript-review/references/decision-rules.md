# Decision Rules

Implemented in `scripts/consolidate_review.py`. Deterministic, so two runs on the same findings
give the same decision.

## Quote verification

Whitespace, `**`, and backticks are normalised on both sides. A quote is verified if it appears
in one line or in a window of up to six consecutive lines (wrapped paragraphs). If it appears
more than once, the occurrence nearest the reviewer's line number is used. Unverified findings
are listed separately and do not count.

## Consensus clusters

Two verified findings belong to the same cluster when their lines are within three of each
other and either one quote contains the other or their title+problem wording overlaps (Jaccard
≥ 0.25 on words of four letters or more). A cluster takes the most severe severity among its
members; `consensus` is the number of distinct roles in it.

In addition, groups listed in the workspace's `merges.json` (lists of `"role:id"`) are joined,
whatever their lines. Clustering is transitive (union-find): if A joins B and B joins C, all
three form one cluster.

## Scorecard

For each dimension: median across roles, and range. Range ≥ 2 is flagged as disagreement.

## Decision

Evaluated in order; the first that applies wins.

| Decision | Condition |
|---|---|
| Reject in current form | a critical cluster raised by ≥ 2 roles; **or** median originality ≤ 2 **and** median significance ≤ 2 |
| Major revision | any critical cluster; **or** ≥ 3 major clusters |
| Minor revision | any major cluster; **or** any heavy machine finding |
| Accept with polishing | none of the above |

"Reject in current form" means the main claim or the contribution needs rethinking before
submission, not that the work is worthless.

## Re-review matching

`diff_review.py` matches an earlier cluster to a later one by quote containment (≥ 12
characters) or, within the same dimension, by title+problem wording (Jaccard ≥ 0.35). Line
numbers are ignored because revision moves them. An earlier cluster with no match counts as
resolved only if at least one of the roles that raised it ran in the later review.
