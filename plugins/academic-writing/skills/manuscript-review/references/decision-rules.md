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

## Submission readiness

Judged separately from the decision and printed first in the report. **READY** only when every
condition holds:

| Condition | Why |
|---|---|
| Decision is not "Reject in current form" | The contribution needs rethinking |
| Editor's `desk_decision.verdict` is `send_to_review` | The gate a submission actually faces first |
| Median significance ≥ 3 and median originality ≥ 3 | 3 = typical solid submission to the target journal; below it the editor is asked to send an under-typical paper out |
| `journal_fit.md` in the workspace | Fit judged from the journal's recent papers, not from memory (`prepare_review.py --fit`) |
| No heavy machine finding | Mechanical blockers |

### Why readiness

The decision is driven by issue clusters, so fixing critical issues turns "Reject in current
form" into "Major revision" even when significance has not moved. In the first long use of this
skill (one author, 27 September – 16 October 2026), 22 panels on five manuscripts never gave a
median significance above 3, and resolving 30 issues between two panels left it where it was.
Three manuscripts went out at median significance 2.0–3.0 — two of them after a last full verdict
of "Reject in current form". The one decided so far was rejected by two journals within five
days without reviewer reports ("does not fit within the scope"); two more were pending. Three
earlier manuscripts by the same author, submitted before the panel existed, were also
desk-rejected for importance or scope. The decision answers "how much revision"; readiness
answers "should this go to that journal now", and only the second is about the gate those
papers failed. `diff_review.py` prints both, and flags a re-review that resolved issues without
raising significance.

## Re-review matching

`diff_review.py` matches an earlier cluster to a later one by quote containment (≥ 12
characters) or, within the same dimension, by title+problem wording (Jaccard ≥ 0.35). Line
numbers are ignored because revision moves them. An earlier cluster with no match counts as
resolved only if at least one of the roles that raised it ran in the later review.
