---
name: scientific-article-writing
description: Workflow for writing a journal article with an AI assistant, from research question to submission and revision — a gated article plan, results files as the only source of numbers, a Markdown manuscript as the single source (Word/PDF are exports), section-by-section drafting in a fixed order, machine checks, a reviewer-style self-review, a submission package (cover letter, declarations, suggested reviewers), and responses to reviewers. Use when the user works on a paper, manuscript, abstract, cover letter, journal choice, desk rejection, or major/minor revision. Triggers in English and Indonesian — paper, article, manuscript, submit, journal, reviewer, rebuttal, revision, abstract, artikel, naskah, jurnal, kirim naskah, revisi mayor, revisi minor, tanggapan penelaah, surat pengantar.
---

# Scientific Article Writing

Respond in the user's language; the manuscript itself is in the journal's language. Integrity
rules — no number without a source, no citation from memory — are in `research-integrity` and
apply in full here. Language checks are in `manuscript-proofreading`.

## Why this skill exists

The pattern that works: a written plan before any prose, numbers only from results files, a
hostile self-review before submission. The failures it prevents are concrete: an abstract
whose count differs from the body; positive and control windows that overlap so the headline
metric collapses exactly where the main claim is made; a paper desk-rejected twice for framing
before anyone reads the results.

## Derivation

```
research question
      ↓
Article plan         A decision · B separation from other papers · C outline · D numbers needed
      ↓
scripts + logs  →  results files        (the only source of numbers)
      ↓
manuscript.md        journal language; editorial notes in ">" blockquotes
      ↓
self-review  →  fixes
      ↓
export (.docx/PDF per journal)  +  submission package
```

The manuscript follows the results, never the reverse. If writing shows the results cannot
carry a claim, **soften the claim or run the experiment** — do not make the sentence cleverer.

## Stages and gates

| Stage | Output | Gate |
|---|---|---|
| 1. Plan | Plan sections A–D | Author approves A (question, answer, genre) and B (separation from other papers) before any prose |
| 2. Results | Results files from scripts that were run; logs kept | Every number in plan D has a source line |
| 3. Outline | Section headings + one claim sentence per subsection | Each claim points to a results file |
| 4. Draft | One section per turn, in the order Methods → Results → Discussion → Introduction → Abstract → Title | Section finished before the next |
| 5. Machine checks | `check_manuscript_en.py`, reference verification (Crossref/arXiv), quote check against PDFs, n-gram overlap | Zero heavy findings; every reference verified |
| 6. Self-review | Dated review file, reviewer style (`references/self-review.md`) | Every critical finding closed or stated in Limitations |
| 7. Package | Journal-formatted export, figures, cover letter, portal texts (`references/submission-package.md`) | Author reads the export; all co-authors approve (ICMJE item 3) |
| 8. After submission | Status note in the manuscript head, status board, commit | Manuscript ID recorded |

**Why the abstract comes last:** it is where numbers most often drift from the body, because it
is written from memory of results. Writing it last, from the final Results, closes that path.

**One section per turn.** A manuscript generated in one pass has uniform rhythm, the most
visible sign of machine prose.

## Anatomy

Title · authors/affiliations · Abstract · Keywords · (Highlights, Elsevier) · Introduction ·
Related work · Data · Methods (with *Use of AI tools* for Springer) · Results · Discussion ·
Limitations · Conclusion · Statements and Declarations · (Declaration of generative AI,
Elsevier — immediately before References) · References · Figure captions.

What each section must contain: `references/manuscript-anatomy.md`.

**Results subsection titles state the claim**, not the topic: "Balancing the test set makes the
ranking irreproducible", not "Ranking results". A reviewer reading only the table of contents
already knows the findings.

## Hard rules

- **Markdown is the manuscript; Word and PDF are exports.** Edit the source, re-export.
  Manuscripts rejected and archived are kept unchanged.
- **Editorial notes in `>` blockquotes**, in any language; exporters and the checker skip them.
- **Visible placeholders** (⬜) for anything uncertain; none may remain at packaging.
- **Target journal's reference style**, not a favourite. Changing journal means restyling every
  reference, then verifying again.
- **Code and derived data released with a DOI** (e.g. Zenodo), version named in the manuscript.
- **No submission without co-author approval, and never on the author's behalf.** The author
  fills in the portal; the assistant prepares copy-paste text.

## Choosing a journal

Read the aims and scope and the guide for authors. Check fees (APC), review model, AI policy,
and that the manuscript is not under review elsewhere. Record the reasons in the plan.

## Rejection and revision

- **Desk rejection:** record the editor's reasons. Decide whether the problem is scope (change
  journal) or framing (rewrite Introduction and title) before resubmitting.
- **Revision:** a response file with one table per reviewer — comment (quoted in full) ·
  response · change in manuscript (section and line). Every changed claim is re-run from
  scripts; no hand-written new numbers. Thank once at the top, then go straight to substance;
  agree when right, disagree with evidence when not.

## When to stop and ask

Plan A/B not approved; results contradict a written claim; overlap with another paper;
target journal, author order, or submit/withdraw decisions; new data needs.

## References

- `references/manuscript-anatomy.md` — required content per section and common failures
- `references/self-review.md` — reviewer-style review before submission
- `references/submission-package.md` — package contents, cover letter, portal checks
