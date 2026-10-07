# Self-Review Before Submission

This stage is not skipped, even under deadline. A reviewer-style pass is where errors that would
invalidate the main claim — leakage, overlapping windows, inverted labels — get caught.

## Stance

Read as a reviewer who wants to reject, not as an author who wants to pass. The core question:
**what single thing, if true, makes the main claim fall?** Look for that first.

## Order

1. **Machine first.** Run and paste the summary into section 0 of the review file:
   - `check_manuscript_en.py` — abstract numbers, citations, table/figure references,
     placeholders, style
   - reference verification against Crossref/arXiv — existence and metadata
   - quote check and n-gram overlap against the cited PDFs
2. **Claim to code.** For every claim in the abstract: find the number in Results → the results
   file → the line of code that produced it. Check the splitting unit, time windows, number of
   repeats, label direction (AUC far below 0.5 almost always means an inverted label).
3. **Cross-section consistency.** The same number in abstract, body, tables, supplement, and plan.
4. **Methods and statistics.** Walk the checklists in
   `third-party/k-dense/common-review-issues.md` (claim–evidence alignment, units, sample size,
   analysis–design fit, prediction and ML) and `third-party/k-dense/statistical-reproducibility-review.md`
   (estimand, denominators, clustered data, multiplicity, reproducibility). MIT, K-Dense Inc.
5. **Confounders.** What distinguishes the classes besides what is claimed? (Database,
   annotator, device, year.)
6. **Tone and genre moves.** Neutralise sentences that attack other authors or sound dramatic;
   a critique is shown on your own models under the standard and the honest evaluation, not by
   naming who erred. Check the genre skeleton in `genre-patterns.md`: gap evidenced (table,
   coded count, degenerate example), same models under two evaluations, cheapest competitor,
   a fence sentence in the abstract.
7. **Compliance.** Reporting guideline, AI policy, the journal's required statements.

## Review file format

`Self_Review_<YYYY-MM-DD>.md`. Per manuscript: **Critical** (claim could fall) → **Major**
(a reviewer will certainly ask) → **Minor**. Each finding: line number, problem, evidence (code
or log re-checked), fix. Findings not yet re-checked against code are marked *not re-checked*.

The review does not edit the manuscript. Fixes go in a separate commit after the author has read
the findings.
