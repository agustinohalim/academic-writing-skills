---
name: thesis-audit
description: Audit a thesis as one connected research chain — skripsi (S1), tesis (S2), or disertasi (S3), in Indonesian or English, from .docx or Markdown. A script converts the document and runs mechanical checks (rumusan masalah ↔ tujuan ↔ kesimpulan counts, citations ↔ daftar pustaka including "dkk.", Tabel/Gambar N.M captions and references, abstract numbers, placeholders); the model then judges fourteen modules along the chain (structure, problem-objective-conclusion chain, gap, literature, method fit, constructs or requirements, data and numbers, analysis and testing, claims, consistency, citations, integrity risk, contribution, dissertation thread); a second script verifies every quote, enforces status and severity rules, and writes a supervisor report, a student feedback sheet ordered upstream-first, and defence questions. Use when supervising a student's skripsi or tesis draft, before a proposal seminar or sidang, when auditing one's own dissertation or doctoral proposal, or when comparing two drafts. Triggers in English and Indonesian — thesis audit, audit my thesis, dissertation check, supervise, defence questions, audit skripsi, periksa skripsi, bimbingan skripsi, draf skripsi mahasiswa, tesis, disertasi, seminar proposal, sidang, pertanyaan penguji, rumusan masalah.
---

# Thesis Audit

Respond in the user's language. Feedback meant for an Indonesian student is written in
Indonesian with "Anda", plain and direct.

## Why this skill exists

A thesis fails along its chain, not in its sentences: a rumusan masalah that no method answers,
a conclusion that answers a different question, a number that changed in chapter IV but not in
the abstract. Reading chapter by chapter misses these, because each chapter looks fine alone.
This skill traces the chain, and leaves the bookkeeping to scripts: a model can judge whether a
method fits a question, but it should not be trusted to count its own findings, check its own
quotes, or grade its own severity. The scripts do that and refuse an audit that does not add up.

Idea credit: the chain-as-system framing, the explicit "not assessable" state, and
reconciliation rules follow ARKANAALZAIR/thesis-debugger (MIT). The code and text are original.

## Flow

```
prepare_audit.py thesis.docx --level skripsi --out <ws>
      → manuscript.md, numbered lines, sections, chain.json, machine.json, AUDIT.md
read the thesis; write <ws>/audit.json          (references/modules.md, audit-schema.md)
report_audit.py <ws>
      → report.md (supervisor) · feedback.md (student) · audit_final.json
next draft: new workspace → impact_review.py <old ws> <new ws> → audit again
```

### 1. Prepare

```bash
python "${CLAUDE_SKILL_DIR}/scripts/prepare_audit.py" <thesis.docx|.md> --level skripsi|tesis|disertasi --out <ws>
```

PDF is not read; ask for the .docx or convert it first (the `pdf` or `docx` skills can help).
Language is detected; force it with `--lang id|en`. Put workspaces outside public repositories —
a student's draft is unpublished work.

Look at the script's summary line before reading: if the chain shows `paragraph` instead of
`list`, or a part is "not found", the headings may be unusual. Check `sections.json` and fix the
headings in `manuscript.md` (then re-run with `--force`) rather than auditing a mis-parsed file.

### 2. Audit

Read `manuscript_numbered.md` in full, then `chain.json` and `machine.json`. Decide
`research_type` first (`references/modules.md` — it changes what "correct" means). Then go
module by module in order, writing `audit.json` (`references/audit-schema.md`).

Rules:
- Every finding quotes the text exactly and has one owning module. The same root cause seen by
  another module goes in `related`, not in a second finding.
- Severity follows evidence: `critical` only when confirmed with high confidence; a `potential`
  issue is at most `minor`. Look for the innocent explanation before escalating.
- A missing input is `not_assessable` with `missing` named, never `not_found`.
- Never invent references, data, or facts about the field. Never call text AI-written or
  plagiarised from style (M12).
- Machine findings are already reported; do not repeat them as findings unless you add judgement
  (a missing reference that also leaves a claim unsupported).
- A supervisor's instructions and the faculty guideline outrank this skill's defaults.

### 3. Report

```bash
python "${CLAUDE_SKILL_DIR}/scripts/report_audit.py" <ws> [--top 12]
```

Exit 1 means the audit is inconsistent: a module missing, a status that contradicts its
findings, a severity the evidence does not carry, a quote not in the text. Fix `audit.json` and
re-run; do not hand over a report with an "inconsistent" section.

- `report.md` — verdict, module matrix, all findings, action plan (upstream first), defence
  questions with the shape of a strong answer. For the supervisor or the author.
- `feedback.md` — skripsi and tesis only: machine fixes, then the top items grouped by chapter,
  then practice questions without answers. For the student, after the supervisor has read it
  (`references/supervising.md`).

### 4. Next draft

Prepare a new workspace, then compare drafts with
`manuscript-review/scripts/impact_review.py <old ws> <new ws>`: chapters edited and not edited,
values changed in one place but left in another. Audit again; keep finding IDs stable for
problems that persist.

## Levels

| Level | Bar | Extra |
|---|---|---|
| `skripsi` | correct, complete work on a real problem; novelty not required | faculty template governs structure |
| `tesis` | sound method, a defensible contribution | literature must reach current work |
| `disertasi` | an original contribution the field did not have | M14 (thread, publications, reuse) — `references/dissertation.md`; also for doctoral proposals |

## Limits

- One reader, one model. The audit finds problems visible in the text; it does not rerun
  analyses, open datasets, or check that references exist (use Crossref tooling).
- The verdict is a rule over counts (any critical → not ready; three or more major → major
  revision), not a prediction of the examiners.
- It is the supervisor's tool. What reaches the student is the supervisor's decision.

## References

- `references/modules.md` — the fourteen modules, research types, severity rules
- `references/audit-schema.md` — the audit.json format
- `references/supervising.md` — rounds, order of work, what not to do, sidang preparation
- `references/dissertation.md` — dissertation level, M14, proposals
- `research-integrity` (AI use, plagiarism, authorship) and `manuscript-proofreading`
  (language) — separate jobs, not part of the audit
