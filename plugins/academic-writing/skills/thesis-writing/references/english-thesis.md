# English-language theses

For a thesis or dissertation written in English: an English-medium programme in Indonesia, a
master's or PhD abroad, or a skripsi the faculty requires in English. The stages, gates, chain
map, and method paths in `SKILL.md` are the same. The other reference files are written in
Indonesian but describe the function of each part, so they apply in any language. This file
covers what changes.

## Structure

The guide (handbook, graduate school regulations, the supervisor's instructions) decides the
chapters. Common layouts, with their Indonesian equivalents:

| Five chapters (common in Indonesia and Asia) | Six chapters (common in UK, Australia, US) | Indonesian |
|---|---|---|
| Chapter 1 Introduction | Chapter 1 Introduction | Bab I Pendahuluan |
| Chapter 2 Literature Review | Chapter 2 Literature Review (or Theoretical Framework) | Bab II Tinjauan Pustaka |
| Chapter 3 Methodology / Research Methods | Chapter 3 Methodology | Bab III Metode Penelitian |
| Chapter 4 Results and Discussion | Chapter 4 Results (or Findings) | Bab IV Hasil dan Pembahasan |
| | Chapter 5 Discussion | |
| Chapter 5 Conclusion and Recommendations | Chapter 6 Conclusion | Bab V Kesimpulan dan Saran |

A thesis by publication (papers as chapters) or a practice-based thesis follows its own rules:
read them before stage 0 and record the structure in the task profile.

When Results and Discussion are separate chapters, the final-thesis order becomes Results →
Discussion → Conclusion → revise Methodology, Literature Review, Introduction → Abstract last.
Results states what the data show without interpretation; Discussion explains, compares with
the literature, and states limitations.

## Terms

| Indonesian | English |
|---|---|
| rumusan masalah | research questions (sometimes problem statement) |
| tujuan penelitian | research objectives / aims |
| hipotesis | hypotheses |
| kerangka berpikir / kerangka konseptual | conceptual framework |
| batasan masalah / ruang lingkup | scope and delimitations |
| manfaat penelitian | significance of the study |
| penelitian terdahulu | previous studies / related work |
| populasi dan sampel | population and sample |
| teknik analisis data | data analysis |
| keabsahan data | trustworthiness (credibility, transferability, dependability, confirmability) |
| kesimpulan / saran | conclusion / recommendations (or implications and future work) |
| abstrak | abstract |
| pedoman | thesis guide / handbook / graduate school regulations |

Keep one English term per concept through the whole thesis and list it in the chain map.
Translating a term differently in two chapters reads as two different constructs to an examiner.

## Placeholders

Write `[NEED: ...]` in an English thesis (`[NEED: sample size from survey_clean.csv]`).
`[PERLU: ...]` and `⬜` are accepted too. The export script and `thesis-audit` treat all of them
as heavy findings.

## Language

- **Tense.** Past for what was done and found (Methodology, Results: "Data were collected…",
  "Scores increased…"). Present for established knowledge, for what tables and figures show, and
  for the thesis's own claims ("Table 4.2 shows…", "These results suggest…"). Future only in a
  proposal's method ("Data will be collected…"); change it to past in the final thesis.
- **Claims sized to evidence.** "Shows" or "demonstrates" only for what was tested; "suggests" or
  "is consistent with" for interpretation; "may" for speculation, used once and labelled as such.
  An association from a survey is not an effect.
- **Spelling.** UK or US, as the guide or institution requires, consistently (analyse/analyze,
  behaviour/behavior, modelling/modeling).
- **Voice.** Follow the field and the supervisor; first person ("I", "we") is accepted in many
  fields and clearer than a long passive. Do not mix "the researcher" and "I" in one thesis.
- **Citations.** The style the guide names (APA 7, Harvard, IEEE, Vancouver). No secondary
  citation when the original is accessible.

Checks: `manuscript-proofreading` (`references/en/academic-english.md`,
`scripts/check_manuscript_en.py`) for language, numbers, and citation-reference agreement;
`research-integrity/scripts/verify_references.py` for the reference list; `thesis-audit` with
`--lang en` for the chain audit.

## Abstract

Usually 250–350 words for a master's or PhD thesis, longer for some doctoral regulations; follow
the guide. One paragraph or structured (Background, Methods, Results, Conclusion) as the guide
says. Written last, from the final results and conclusion; every number appears in the body.
