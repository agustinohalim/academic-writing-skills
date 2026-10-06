# What Editors and Reviewers Check

"Scopus-indexed" describes the journal, not a review standard. Each journal's editor and reviewers
decide, but the criteria are much the same across Elsevier, Springer Nature, Wiley, and IEEE. A
manuscript passes two gates; write for both.

## Gate 1 — the editor's desk screen

Between 30 and 70 % of submissions end here, without external review. In order of frequency:

1. **Out of scope** for the journal's aims or readership — reported as 40–50 % of desk rejections.
   Read the aims and two or three recent papers before choosing the journal.
2. **Too little novelty or contribution** for that journal: the paper does not advance what is
   already known enough to justify the space.
3. **Methodological or statistical flaws visible on a first read** — flaws no revision would fix,
   or conclusions the data do not support.
4. **A weak abstract.** It is the first and often the only part the editor reads before deciding.
5. **Non-compliance and presentation**: author instructions not followed, length, language that
   obscures meaning, missing declarations, ethics, or trial registration.

Editors usually give three or more reasons at once; a desk rejection that names only "scope" or
"importance" is still a judgement on the contribution.

## Gate 2 — the reviewers

Elsevier's reviewer guidance asks, per section:

| Part | Question the reviewer answers |
|---|---|
| Title | Does it accurately and sufficiently describe the content? |
| Abstract | Does it reflect all essential aspects, including major results and limitations? |
| Introduction | Is the background current; are the objectives clearly stated? |
| Methods | Detailed enough to replicate; statistics reported accurately; methods match the question? |
| Results | Is the presentation (tables, figures) appropriate? |
| Discussion | Are interpretation and conclusions supported by the data? |
| References | Up to date and relevant? |
| Language | Does it need editing? |
| Overall | Is the research novel or important? Any ethical or integrity concern? |

Springer Nature adds the grounds for rejection: specialist interest only, **lack of novelty,
insufficient conceptual advance**, or major technical or interpretational problems. Reviewers
comment on importance and novelty because that is what helps the editor most.

## Journal-specific exclusions — read them before writing

Many journals list what they will not consider. Example, *Computers in Biology and Medicine*
(Elsevier): the novelty must be clear **in the first two pages**; the journal does not accept
papers with minor architecture or model modifications and only a slight performance gain, or
with unclear division of data into training, validation, and test sets. Copy the exclusion list
of the target journal into the article plan and check the manuscript against it.

## The "solves nothing" trap

A paper whose whole contribution is that existing practice is flawed — a benchmark audit, a
leakage demonstration, a negative result — answers the reviewer's novelty question but not the
editor's importance question: *what can the reader now do that they could not before?* Repeated
desk rejections for "importance" or "scope" on such papers are the signature of this trap.

Ways out, strongest first:

1. **Pair the critique with a constructive result.** Solve the task properly — a model, protocol,
   or tool that works under the stricter evaluation — and use the audit as the evidence that the
   result is real. The audit moves from the headline to the Methods and Results as validation.
2. **Turn the critique into a tool others will use**: a test suite, a corrected benchmark with a
   leaderboard, a reporting checklist that changes how papers are reviewed.
3. **Show the consequence**: a decision, ranking, or clinical or policy conclusion that changes
   once the flaw is fixed, with numbers.

A critique alone is still publishable in venues that explicitly welcome it (methods, reproducibility,
or negative-results tracks), but it should not be the only kind of paper in a portfolio.

## Checklist before choosing to write

- [ ] The paper's one-sentence contribution answers "what can the reader now do?"
- [ ] The target journal's aims match it; its exclusion list does not hit it.
- [ ] The novelty is visible on page 1–2 and in the abstract.
- [ ] Splits, baselines, and statistics would survive a first read by a methods-minded editor.
- [ ] Conclusions claim no more than the data show.

## Sources (checked 6 October 2026)

- Elsevier — How to review. https://www.elsevier.com/reviewer/how-to-review
- Elsevier Connect — How to review manuscripts. https://www.elsevier.com/connect/how-to-review-manuscripts
- Springer Nature (EMBO Press) — Reviewer guidelines. https://link.springer.com/partners/embo-press/editorial-policies/reviewer-guidelines
- Springer Nature — How to peer review. https://www.springernature.com/gp/authors/campaigns/how-to-peer-review
- Jawaid SA, Jawaid M (2019) Common reasons for not accepting manuscripts for further processing
  after editor's triage and initial screening. *Pak J Med Sci* 35(2). https://pmc.ncbi.nlm.nih.gov/articles/PMC6408665/
  — 70–80 % not processed further at that journal; cites Meyer et al. (2018), *Academic Medicine*:
  rejected manuscripts had on average three or more reasons.
- Editage Insights — From desk rejection to revision: what editors wish authors knew.
  https://www.editage.com/insights/from-desk-rejection-to-revision-what-editors-wish-authors-knew
  — scope mismatch 40–50 % of desk rejections; desk rejection 30–70 % of submissions (secondary
  source; treat the ranges as indicative).
- *Computers in Biology and Medicine* — Guide for authors. https://www.sciencedirect.com/journal/computers-in-biology-and-medicine/publish/guide-for-authors
  (exclusion text quoted from a search summary; the page returned 403 to automated fetch — verify
  against the live guide before relying on the wording.)
