# Journal Metrics

Metrics narrow a list; they do not choose a journal. Fit comes first.

## What each one is

| Metric | Producer | Database | Counts | Where to read it |
|---|---|---|---|---|
| **CiteScore** | Elsevier | Scopus | Citations received in years Y−3…Y by articles, reviews, conference papers, book chapters, and data papers published in Y−3…Y, divided by the number of those documents; every citation weighs the same. Four-year window since the 2020 method change — older values are not comparable | `scopus.com/sources` (free), with a **percentile** within each subject category; CiteScore Tracker updates monthly |
| **SJR** | SCImago (CSIC and University of Granada), not Elsevier | Scopus data | Citations (three-year window) weighted by the prestige of the citing journal | `scimagojr.com` (free), shown as **quartile** Q1–Q4 per category |
| **SNIP** | CWTS Leiden | Scopus data | Citations per paper (three-year window) divided by the citation potential of the journal's field; 1.0 ≈ the median journal. Better than CiteScore for comparing across fields | `scopus.com/sources`; `journalindicators.com` |
| **Journal Impact Factor** | Clarivate | Web of Science | Citations in one year to items of the two previous years | Journal Citation Reports (subscription); many journals show it on their homepage |

## Getting the values in bulk

Scimago offers the whole ranking as one file (`scimagojr.com/journalrank.php?out=xls`, semicolon
separated: title, ISSN, publisher, open access, SJR, SJR Best Quartile, H index, coverage,
categories). The site sits behind a bot check, so a plain download from a script is refused; it
works from a normal browser session. Record the edition year (the file's document-count column
names it).

## Quartile traps

- **"Q1" without a name means nothing.** A journal can be Q1 by CiteScore percentile and Q2 by
  SJR, because the metrics, the category definitions, and the coverage differ. Always write the
  metric and year: "SJR 2025 Q2 (Computers in Earth Sciences)".
- **Quartiles are per category.** A journal in several categories can hold different quartiles
  in each. A narrow category's Q1 is the top quarter of a small group.
- **Values move every year.** A rung chosen on last year's quartile may fall a quartile by the
  time the paper is published. Leave a margin if a threshold matters.
- **Scopus indexing and SJR are not the same thing.** SJR is computed from Scopus data but can
  lag; a title discontinued by Scopus may still show on Scimago for a while.

## Old guides go stale

Elsevier's own booklet *How to publish in scholarly journals* (still downloadable from Researcher
Academy, written around 2016) describes CiteScore with a three-year window and credits the Impact
Factor to Thomson Reuters. Both are out of date: CiteScore moved to four years in 2020 and the
Impact Factor is now Clarivate's. Take metric definitions from the producer's current page, not
from a training PDF.

## Which metric counts

Institutions and regulations name a specific metric and threshold (for example, "Q4 SJR with SJR
> 0.1", or a national index such as SINTA). Read the regulation's own wording, check that exact
metric at its source, and record the year of the value. Do not substitute a metric the journal
advertises on its homepage.

## Using metrics without being used by them

- A high Impact Factor or CiteScore often comes with a high rejection rate (Elsevier, *Aim high,
  but aim realistic*). Rung 1 is chosen by fit, then reach.
- Acceptance rate and time to first decision matter as much as rank when a deadline exists.
  Elsevier JournalFinder and IEEE Publication Recommender show some of these; otherwise use the
  journal's own "insights" page where it publishes them.
- A metric jump in one year, with a jump in output, is a reason to check the journal more
  closely, not a reason to choose it (see `verification.md`).
