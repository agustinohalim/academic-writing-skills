---
name: manuscript-proofreading
description: Proofreading and copy-editing for academic text in Indonesian (EYD Edisi V, KBBI, italic foreign terms, "Anda" register) and English (journal manuscripts) — runs deterministic checkers first (scripts/check_manuscript_en.py for English manuscripts, scripts/periksa_gaya.py for Indonesian machine-prose patterns), then reads in layers: consistency of numbers and terms, sentences, spelling and punctuation, formatting. Corrects errors without rewriting the author's voice. Use when asked to proofread, copy-edit, check spelling or grammar, tidy up, check before submission or printing, or when text "sounds AI-written"; also when a document, chapter, or manuscript is declared finished. Triggers in English and Indonesian — proofread, copy-edit, grammar, spelling, sunting, koreksi, periksa ejaan, periksa bahasa, rapikan, EYD, KBBI, terasa seperti tulisan AI.
---

# Manuscript Proofreading

Respond in the user's language. Language-specific rules: `references/id/ejaan-eyd-v.md` for
Indonesian, `references/en/academic-english.md` for English.

## Why this skill exists

Proofreading with an AI assistant has two proven traps.

**The editor who rewrites.** Paraphrasing tools "improve" prose on every pass, and the first
casualties are the things that must not move: tables, section labels, figure numbers, code,
defined terms. Editing here is therefore **narrow and traceable**: fix errors, do not replace
the author's voice.

**A clean checker taken as proof of good prose.** A pattern checker only proves that the
patterns it knows are absent. Authors develop their own tics — a word used fifteen times in
14,000 words — that no list contains. The rest has to be read.

## Principles

1. **Fix, don't rewrite.** Every edit has a nameable reason: misspelling, wrong number,
   ambiguity, banned pattern, inconsistency. "Sounds better" is not a reason.
2. **Structure is untouchable.** Metadata tables, section headings, figure/table numbers,
   exercise numbers, code blocks, identifiers, and editorial notes stay exactly as they are.
3. **Content does not change through editing.** Findings that touch content — a wrong number,
   an overclaim — are reported, not silently fixed (see `research-integrity`).
4. **Locked files are not edited**: archived submissions, dated forecasts, deliberately broken
   teaching files, exported `.docx`/`.pdf` (edit the source instead).
5. **Printed code is run** if an edit touches a code block or its output.

## Layers

Work top-down; errors in upper layers make lower-layer work wasted.

| Layer | What | Tool |
|---|---|---|
| 0. Machine | Banned patterns, leftover placeholders, abstract numbers, citations, table/figure references | `check_manuscript_en.py` (English), `periksa_gaya.py` (Indonesian) |
| 1. Consistency | Same number everywhere; one term per concept; file names, figure numbers | Read + search |
| 2. Sentences | Ambiguity, missing subject, uniform rhythm, words repeated > 3 per 1,000 | Read aloud |
| 3. Spelling and punctuation | EYD V / KBBI; one English variant (British or American) | References |
| 4. Formatting | Italics for foreign terms, bold, lists, dashes, spacing | Read |

## Running the checkers

```bash
# English manuscript (Markdown)
python "${CLAUDE_SKILL_DIR}/scripts/check_manuscript_en.py" manuscript.md
python "${CLAUDE_SKILL_DIR}/scripts/check_manuscript_en.py" --heavy --no-markers draft.md

# Indonesian prose
python "${CLAUDE_SKILL_DIR}/scripts/periksa_gaya.py" bab_02.md
python "${CLAUDE_SKILL_DIR}/scripts/periksa_gaya.py" --semua --berat     # all .md under the working folder
```

Python 3.10+, standard library only. Both exit with status 1 on **heavy** findings, which must
reach zero before a document is called finished. **Light** findings are read one by one — some
are correct as written (a table naming a student mistake is not the author's puffery). In
Indonesian files, `<!-- gaya:abaikan -->` on the preceding line silences a legitimate case.

`check_manuscript_en.py` expects `## Abstract` and `## References` headings, reads paragraphs
rather than lines, and skips `>` blockquotes (use them for editorial notes). "Table N has a
caption but is never cited" is a real error: typesetters place a table near its first citation.

**Adding patterns.** A tic found while reading goes into the checker — `scripts/pola/claudish_id.json`
for Indonesian, `KATA_MESIN` in `check_manuscript_en.py` for English — not into memory. Do not
replace the Indonesian rule file with a translated English list; Indonesian machine prose has its
own patterns.

## Output

Small edits (≤ 10, no content change): edit directly, then list each change — line,
before → after, one-word reason (spelling / number / pattern / consistency).

Large edits, or someone else's file (co-author, submitted manuscript): **do not edit**. Produce
the same list and let the author decide.

Re-run the checkers afterwards. Rebuild derived files (`.docx`, `.pptx`, PDF) from source.

## When to stop and ask

- The needed edit changes meaning, a number, or a claim.
- A term differs from the source document it derives from — which one is right?
- The file belongs to a co-author or has already been submitted.
- The author deliberately uses a non-standard form (a quote, a named mistake, field jargon).

## References

- `references/id/ejaan-eyd-v.md` — EYD V and KBBI rules most often missed (Indonesian)
- `references/en/academic-english.md` — numbers, tenses, terminology, claims, tone
- `scripts/check_manuscript_en.py`, `scripts/periksa_gaya.py`, `scripts/pola/claudish_id.json`
