# Manuscript Anatomy

Required content per section and the failures that recur. Reporting guidelines (REFORMS,
TRIPOD+AI) are in the `research-integrity` skill.

## Head

- Title: a claim or question, not a topic. Avoid the "X, not Y" construction in titles.
- Authors, full affiliations with address, corresponding author, email, ORCID.
- A `>` status note (any language): date, target journal / manuscript ID, which results file
  feeds which section, binding decisions. Exporters drop it.

## Abstract

- Journal word limit — count it.
- Problem → data and design → findings with numbers → implication. No citations.
- **Every number in the abstract appears identically in the body.** Ranges written the same way
  in both places.
- Claims limited to what was tested.

## Introduction

Three core paragraphs: prevailing practice → what is not yet known or tested (verified
citations) → what this paper does and finds. End with a numbered contribution list if the
venue uses one. No "In recent years, … has attracted increasing attention".

## Related work

Grouped by idea, not by paper. Each group ends with this paper's position relative to it.
A co-author who wrote a discussed paper is declared under competing interests.

## Data

Source, period, unit (district-month, recording, patient), filtering with counts before and
after, download date, product versions. Patients and recordings reported separately.

## Methods

- Models, including simple baselines.
- Data splitting: grouping unit, scheme (rolling origin, leave-one-group-out), and when
  preprocessing is computed (per fold).
- Metrics, confidence intervals (bootstrap repeats **equal to the code**), comparison tests.
- Springer: *Use of AI tools* subsection here.
- Every parameter named in the text matches the code.

## Results

Claim-style subsection titles. Each subsection: claim → numbers → table/figure cited → one
sentence on the limit of the claim. Every table and figure is **cited in the text** before it
appears. Negative results reported as results.

## Discussion

What the findings mean for practice → why (mechanism, tested if possible) → relation to
literature → a checklist or recommendation readers can use. Do not re-list Results numbers.

## Limitations

A section of its own, specific and honest: known confounders (e.g. different annotation
processes between classes, ceiling effects), unavailable data, and claims **not** supported.

## Statements and Declarations

| Item | Content |
|---|---|
| Funding | If none, the journal's standard sentence |
| Competing interests | Including co-authors who wrote criticised or audited work |
| CRediT | Roles per author, decided by the authors |
| Data availability | **Every** data source with link/DOI; derived data on a repository |
| Code availability | Repository/DOI + the version that produced the numbers |
| Ethics | Open de-identified data: licence, and whether ethics approval is required per the journal |
| AI | Elsevier: separate section before References. Springer: in Methods |

## References

Journal style. DOIs where available. Every entry cited, every citation listed
(`check_manuscript_en.py`); every entry real with matching metadata (Crossref/arXiv check).

## Figure captions

One per figure, understandable without the text: what is plotted, units, abbreviations,
sample size, meaning of lines/points/bands.
