---
name: thesis-writing
description: Drafting a skripsi (S1), tesis (S2), or disertasi (S3), or an English-language master's thesis or PhD dissertation, chapter by chapter — Bab I to Bab V or Chapter 1 to 5/6, proposal or final — together with the author, from the author's own material (approved proposal, notes, data, results files, interview transcripts, test logs). A task profile from the campus guide (pedoman) comes first, then a chain map (rumusan masalah ↔ tujuan ↔ hipotesis ↔ metode ↔ analisis ↔ kesimpulan) before any prose, then one chapter per turn in a fixed order — proposal Bab III → II → I, final Bab IV from results files → V → revise III/II/I → abstrak last — with method paths for quantitative, qualitative, R&D / system development, and mixed methods, and export of the Markdown chapters to DOCX and PDF in the campus format. Use when the user writes or revises a thesis or thesis proposal, or one of its chapters or sections. Triggers in English and Indonesian — write thesis, thesis chapter, thesis proposal, master's thesis, PhD dissertation, dissertation chapter, introduction chapter, literature review, methodology chapter, research questions, results chapter, findings, discussion chapter, conclusion chapter, export thesis to Word or PDF, tulis skripsi, menulis skripsi, proposal skripsi, Bab I, Bab II, Bab III, Bab IV, Bab V, latar belakang, rumusan masalah, tujuan penelitian, tinjauan pustaka, kajian teori, kerangka berpikir, metode penelitian, hasil dan pembahasan, kesimpulan dan saran, abstrak, ekspor DOCX, ekspor PDF, format pedoman kampus.
---

# Thesis Writing

Respond in the user's language; the thesis itself is in the language the faculty requires.
Integrity rules — no number without a source, no citation from memory — are in
`research-integrity` and apply in full here. Language checks are in `manuscript-proofreading`.
The audit of a finished draft is `thesis-audit`.

**English-language theses** follow the same stages. Chapter names, the five- or six-chapter
layout (Results and Discussion as separate chapters), the term map (rumusan masalah → research
questions), tense and hedging, and `[NEED: ...]` placeholders are in
`references/english-thesis.md`. The other reference files are in Indonesian but describe what
each part must do, so they apply in either language.

## Why this skill exists

A thesis is usually written in chapter order, I to V, and that order is the cause of most of its
defects. Bab I promises what the data later cannot deliver; Bab II reviews theories that no
method ever uses; Bab V answers questions phrased differently from the rumusan masalah; the
abstract quotes a number from an earlier analysis. Each chapter reads well alone, so nobody sees
the break until the examiner does.

This skill fixes the chain first and writes the prose around it. Chapters that depend on results
are written from results files, and the chapters that frame the work are revised after the
results are known, so they promise only what was delivered.

## Who writes

The author does the research and owns the text. The assistant drafts from the author's material,
asks for what is missing, and marks every gap visibly. It does **not** produce a thesis for
someone who did not do the research (joki, ghostwriting), invent respondents, interviews, data,
test results, or quotations, or write a chapter whose substance the author has not supplied.
If the request is "write my skripsi" with no data and no approved proposal, say so plainly and
offer what can honestly be done: help shape the proposal, plan the method, or explain a section.

AI use is disclosed the way the campus requires (a statement in the preface, a declaration page,
or a methods note). If the pedoman is silent, tell the author to ask the supervisor and keep a
record of what the assistant did. Rules: `research-integrity`.

## Derivation

```
campus pedoman + level              → task profile (structure and format variables)
approved proposal / research plan   → chain map  (rumusan ↔ tujuan ↔ hipotesis ↔ metode ↔ analisis ↔ kesimpulan)
      ↓
PROPOSAL   Bab III → Bab II → Bab I                    (method decides what theory is needed)
FINAL      data → scripts / coding / test logs → results files
           Bab IV from results files → Bab V → revise Bab III, II, I → abstrak last
      ↓
self-check per chapter  →  thesis-audit  →  manuscript-proofreading  →  export (DOCX / PDF)
```

Prose follows the chain, never the reverse. If writing shows the data cannot answer a rumusan,
**change the rumusan with the supervisor or collect what is missing** — do not make the sentence
vaguer.

## Stages and gates

| Stage | Output | Gate |
|---|---|---|
| 0. Task profile | Level (skripsi / tesis / disertasi), proposal or final, research type, language, and the structure and format variables read from the pedoman (`references/pedoman-kampus.md`). A variable the pedoman does not settle is written `[PERLU: pedoman]` with the default shown | Author confirms the profile. No pedoman → defaults, every one marked to confirm |
| 1. Chain map | One table: each rumusan masalah → its tujuan → hipotesis (if any) → data and method that answer it → analysis → where the answer will appear in Bab IV and V. Method path chosen (`references/jalur-metode.md`) | Every rumusan has a method that can answer it and data that exists or can be collected. Author approves before any prose |
| 2. Chapter plan | For the next chapter: headings from the profile + one sentence per subsection saying what it establishes, and which source or file it rests on | Each sentence points to a source, a results file, or the chain map |
| 3. Draft | One chapter (or one long section) per turn, in the order above. Bab I–III: `references/bab-i-iii.md`. Bab IV–V: `references/bab-iv-v.md` | Self-check of the chapter passes before the next one starts |
| 4. Revise frame | Final only: Bab I, II, III re-read against what Bab IV actually shows; promises cut or kept; method text matches what was done, deviations stated | Chain map updated; no rumusan without an answer in Bab V |
| 5. Abstrak | Written last, from the final Bab IV and V; numbers copied from them, not from memory | Every number in the abstract appears in the body |
| 6. Hand-off | `thesis-audit` before seminar proposal or sidang, `manuscript-proofreading` for EYD V and language, reference check (`research-integrity/scripts/verify_references.py`) | Zero heavy machine findings; supervisor has read the audit |
| 7. Export | DOCX and/or PDF in the campus format (`references/ekspor.md`) | Export refuses leftover placeholders unless it is a draft |

**One chapter per turn.** A thesis generated in one pass has uniform rhythm and uniform
emptiness. Writing a chapter at a time keeps each one tied to its sources and lets the author
correct the direction early.

**Why Bab III first in a proposal:** the method decides what Bab II needs (the constructs, the
model, the standards, the comparison) and what Bab I may promise. A literature review written
first collects theories that the method never touches.

**Why Bab IV first in the final thesis:** the results are fixed by the data; everything else is
framing. Writing Bab IV first from the results files, then Bab V from Bab IV, then revising the
frame, is the only order in which the abstract, the conclusions, and the rumusan can agree.

## Self-check per chapter

Before moving on, check and report in two or three lines:

- Every number traces to a results file, a table in the thesis, or a cited source. Missing ones
  are `[PERLU: angka dari <file>]`, never estimated.
- Every citation was retrieved (Crossref, OpenAlex, Garuda, SINTA, the PDF, the publisher page),
  not recalled. Unchecked ones are `[PERLU: verifikasi sitasi]`.
- Terms match the chain map and earlier chapters (one name per variable, one name per system).
- Rumusan, tujuan, and (in Bab V) kesimpulan still match one to one, or the mapping is stated.
- Tabel and Gambar are numbered per chapter (Tabel 4.2) and referred to in the text.
- Placeholders that remain are listed for the author.

## Placeholders

Use `[PERLU: ...]` for anything the author must supply or confirm
(`[PERLU: jumlah responden dari data_kuesioner.xlsx]`, `[PERLU: pedoman — jarak spasi abstrak]`);
in an English thesis, `[NEED: ...]` (`[NEED: sample size from survey_clean.csv]`). `⬜` is
accepted too. `thesis-audit` and the export script treat leftover placeholders as heavy
findings, so they cannot reach the supervisor or the examiner unnoticed.

## Method paths

The research type changes what Bab III must state, what Bab IV must report, and what Bab V may
claim. Pick the path from what the study actually does, not from the faculty's default template:

- **Kuantitatif** — survey, experiment, quasi-experiment, correlational, comparative.
- **Kualitatif** — case study, phenomenology, ethnography, grounded theory, narrative.
- **R&D / pengembangan** — Borg & Gall, ADDIE, 4D, Plomp; system development in informatics
  (waterfall, prototyping, RAD).
- **Campuran** — convergent, explanatory sequential, exploratory sequential.

Details per path: `references/jalur-metode.md`. Do not force hypotheses onto qualitative work,
saturation onto a survey, or effectiveness claims onto a product that was only validated.

## Levels

| Level | Bar | Extra |
|---|---|---|
| `skripsi` | correct, complete work on a real problem; novelty not required | faculty template governs structure |
| `tesis` | sound method and a defensible contribution | literature reaches current work (last five to ten years, as the pedoman says) |
| `disertasi` | an original contribution the field did not have | the novelty statement and the thread through publications are planned in stage 1; see `thesis-audit/references/dissertation.md` |

## Export

```bash
python "${CLAUDE_SKILL_DIR}/scripts/ekspor_naskah.py" bab/ --out Skripsi_Budi --docx --pdf
python "${CLAUDE_SKILL_DIR}/scripts/ekspor_naskah.py" bab_1.md bab_2.md bab_3.md --out Proposal --docx --draft
```

The Markdown chapters are the source; DOCX and PDF are exports. Page size, margins, font, size,
and line spacing come from the task profile. Requires pandoc; PDF additionally needs LibreOffice,
Typst, or a LaTeX engine. Details and citeproc with `.bib` + CSL: `references/ekspor.md`.

## When to stop and ask

- A rumusan masalah has no data or method that can answer it.
- The results contradict a hypothesis or a claim already written in Bab I or the abstract.
- The pedoman and the supervisor's instructions disagree (the supervisor's written instruction
  usually wins; ask).
- A number, quotation, or respondent detail is needed and no file contains it.
- The request amounts to writing the thesis for someone who did not do the research.

Say it in one or two sentences, put a placeholder in the text, and continue with work that does
not depend on the answer.

## Limits

- The assistant drafts from what it is given. It does not run the study, collect data, or
  interview anyone; analysis is run by the author's scripts or software and read from files.
- The structure follows the pedoman and the supervisor. This skill's defaults are a starting
  point, not a rule of any campus.
- A draft that passes the self-check can still be wrong about the field. Supervisor review and
  `thesis-audit` are not optional.

## References

- `references/pedoman-kampus.md` — structure and format variables, Indonesian defaults to confirm
- `references/bab-i-iii.md` — Bab I to III: what each section must do, failures, proposal specifics
- `references/bab-iv-v.md` — Bab IV and V: results from files, discussion, conclusions, suggestions
- `references/jalur-metode.md` — quantitative, qualitative, R&D, and mixed-method paths
- `references/ekspor.md` — export script, requirements, citations
- `references/english-thesis.md` — English-language theses: chapter layouts, terms, tense,
  placeholders, abstract
- `thesis-audit` (chain audit before seminar or sidang), `manuscript-proofreading` (EYD V, KBBI),
  `research-integrity` (citations, AI disclosure, plagiarism)
