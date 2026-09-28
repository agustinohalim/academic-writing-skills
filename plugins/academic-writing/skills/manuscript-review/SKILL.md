---
name: manuscript-review
description: Simulated pre-submission peer review of a Markdown manuscript by a panel of five independent roles — editor/journal fit, methods and statistics, domain and literature, presentation, and devil's advocate — with every finding tied to an exact quote and line, quotes verified by script, consensus detected across roles, a seven-dimension scorecard, a rule-based decision, a revision roadmap, and a re-review diff after revision. Use before submitting a paper, after a desk rejection or a mid external score, or to check a revision against an earlier review. Triggers in English and Indonesian — review my paper, peer review, referee report, simulate reviewers, pre-submission review, re-review, telaah naskah, tinjau naskah, simulasi penelaah, telaah sebelum kirim, telaah ulang revisi.
---

# Manuscript Review

Respond in the user's language; findings quote the manuscript in its own language.

## Why this skill exists

A self-review done in one pass by one voice finds what that voice already believed. Journals
use several reviewers with different jobs because each catches a different class of problem: the
editor asks whether the paper matters to this readership, the methods reviewer whether the
numbers can be trusted, the domain reviewer whether it is new, the devil's advocate whether the
main claim survives its strongest objection. This skill reproduces that division of labour and
adds what human panels lack: every finding must quote the manuscript exactly, and a script
throws out findings whose quote is not there.

It does not replace real reviewers, and its scores are not a prediction of acceptance.

## Flow

```
prepare_review.py  →  workspace (frozen copy, numbered lines, sections, machine findings)
        ↓
panel: five roles, each reading independently, each writing findings/<role>.json
        ↓
consolidate_review.py  →  quote verification · consensus clusters · scorecard · decision · report.md
        ↓
author revises  →  prepare_review.py again (new folder)  →  panel  →  consolidate
        ↓
diff_review.py old new  →  resolved · still open · not re-checked · new
```

### 1. Prepare

```bash
python "${CLAUDE_SKILL_DIR}/scripts/prepare_review.py" manuscript.md --out review/<YYYY-MM-DD>
```

The workspace freezes the manuscript (SHA-256 recorded), numbers its lines, maps headings to
line ranges, and runs `check_manuscript_en.py` from `manuscript-proofreading`. Heavy machine
findings become submission blockers in the report. Put the workspace next to the manuscript,
not in the plugin folder.

### 2. Configure the panel

Read the manuscript once and write a short `PANEL.md` addition naming, for each role, the
concrete expertise it should take — "a reviewer who evaluates spatial cross-validation in
remote-sensing ML", not "a methods expert" — and the target journal if known. Show it to the
author and adjust before running the roles. Role definitions: `references/roles.md`.

### 3. Run the roles independently

Each role reads `manuscript_numbered.md` and writes `findings/<role>.json` following
`references/finding-schema.md`. **Roles must not see each other's output before writing their
own** — independence is what makes agreement meaningful.

- If this session can run subagents, run the five plugin agents in parallel:
  `review-editor`, `review-methods`, `review-domain`, `review-presentation`,
  `review-devils-advocate`. Give each the workspace path and the panel note for its role.
- Otherwise run them one at a time in this session, writing each file before reading the next
  role's definition, and never re-opening earlier role files.

Rules every role follows: quote exactly (copy text, never paraphrase into the quote field); one
problem per finding; severity by consequence (`critical` = a main claim may be wrong or
unsupported; `major` = a reviewer will certainly require it; `minor` = improves the paper);
say what to do in `fix`; no invented references, numbers, or facts about the field — if a
missing reference is suspected, describe what kind of work is missing instead of naming one.

### 4. Consolidate

```bash
python "${CLAUDE_SKILL_DIR}/scripts/consolidate_review.py" review/<YYYY-MM-DD>
```

The script merges findings automatically only when they quote the same passage. Different
roles often raise **the same issue at different places** (the abstract's claim, the Discussion's
restatement, the Limitations paragraph); word overlap cannot tell those from distinct issues
reliably. So after the first run, read all role files together and write
`review/<date>/merges.json` — a list of groups of `"role:id"` that are the same issue:

```json
[["editor:X6", "methods:M5", "devils-advocate:X7"], ["methods:M1", "devils-advocate:X5"]]
```

Merge only when a single fix would answer every member. Then run the script again. The file
stays in the workspace, so the merge decisions are visible and can be challenged; unknown IDs
are reported as errors. In the first real run (a 6,300-word manuscript, 65 findings) this
changed the result from 56 clusters with 8 consensus issues to 38 clusters with 15.

Then read `report.md` with the author. Findings "set aside" had quotes not found in the
manuscript: check whether the reviewer misquoted (fix and re-run) or hallucinated (discard).
Decision rules and scorecard: `references/decision-rules.md`.

### 5. Re-review after revision

Prepare a **new** workspace on the revised manuscript, run the roles again (all of them, or at
least the ones that raised critical or major issues), consolidate, then:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/diff_review.py" review/<old> review/<new>
```

Issues whose roles did not run again are reported as *not re-checked*, never as resolved.

## What the author does with the report

Work the revision roadmap from the top. Consensus issues first; a critical issue from a single
role deserves a direct answer (fix it or explain why it does not apply) because journal
reviewers raise exactly those. Scores that the roles disagree on (range ≥ 2) mark places where
the paper reads differently to different readers — usually a framing problem.

## Limits

- One model playing five roles shares one set of blind spots. Treat consensus as "likely", not
  "certain", and a clean report as "no obvious problems", not "ready".
- The skill checks the manuscript against itself. It does not verify that references exist
  (use Crossref/arXiv tooling), rerun analyses, or check data.
- Do not upload confidential or embargoed manuscripts to external services to run this; it runs
  locally on the Markdown file.

## References

- `references/roles.md` — what each role examines and the questions it must answer
- `references/finding-schema.md` — the JSON each role writes
- `references/decision-rules.md` — how clusters, scores, and the decision are computed
- `scientific-article-writing/references/pre-submission-scorecard.md`,
  `story-and-structure.md`, and `third-party/k-dense/*` — checklists the roles draw on
