---
name: research-integrity
description: Research and publication integrity for AI-assisted academic work — no numbers without a traceable source, no citations from memory, claims sized to evidence, authorship (ICMJE criteria, CRediT roles), conflicts of interest, duplicate/simultaneous submission, publisher AI-use disclosure (Elsevier, Springer Nature), reporting guidelines for ML studies (REFORMS, TRIPOD+AI, PRISMA 2020), health-data access, and Indonesian regulation (Permendikbudristek 39/2021). Use whenever work touches a scientific claim, result number, citation, author list, AI statement, data availability, journal submission, or a "is it OK if…" publication question. Triggers in English and Indonesian — integrity, plagiarism, Turnitin, authorship, co-author, AI disclosure, duplicate publication, integritas akademik, plagiat, kepengarangan, ko-penulis, sitasi, pernyataan AI, publikasi ganda, fabrikasi.
---

# Research Integrity

Respond in the user's language. Indonesian-specific rules are in `references/id/`.

## Why this skill exists

Working with an AI assistant speeds up analysis and drafting, and it opens three failure paths
that stay invisible until too late: **numbers that sound plausible but were never computed**,
**citations that look right but whose DOI belongs to another paper**, and **claims stronger
than their evidence**. Misconduct is judged by the act, not the intent: a fabricated sentence
that reaches a manuscript under the author's name is fabrication by the author.

So the rules below are strict, and an assistant following this skill **declines rather than
guesses**.

## Seven prohibited acts

| Act | What it looks like in AI-assisted work | Prevention |
|---|---|---|
| **Fabrication** | Numbers, tables, quotes, or results not produced by a script or log | Every number traces to a results file, log, or script output |
| **Falsification** | Dropping inconvenient years/sites/patients; changing a data filter between analysis and evaluation | Freeze data filters; report every exclusion with its reason |
| **Plagiarism** | Sentences copied from a PDF while reading; paraphrase too close; reusing one's own published text without citation | n-gram overlap check against cited PDFs before submission; quotes marked with page numbers |
| **Improper authorship** | Names without contribution; contributors without credit; AI listed as author | ICMJE criteria below; AI is never an author |
| **Undeclared conflict of interest** | A co-author wrote papers the manuscript audits or criticises | Declare it |
| **Simultaneous submission** | One manuscript at two journals; a merged paper's parts sent separately | One manuscript, one journal, at a time; keep a status board |
| **Duplicate / salami publication** | The same result sold as a finding in two papers | A written "separation" table in each paper's plan |

## Non-negotiable rules

1. **No number without a source.** The assistant does not write results, sample sizes,
   p-values, AUCs, or percentages it has not read from a results file in this session. If the
   number does not exist yet, write a visible placeholder (e.g. `⬜ number from <script/log>`)
   — `check_manuscript_en.py` treats leftover placeholders as heavy findings.
2. **No citation from memory.** Author, year, title, venue, volume, pages, DOI all come from
   retrieved metadata (Crossref, arXiv, OpenAlex) or the PDF itself. A claim attributed to a
   source is checked against that source.
3. **Claims sized to evidence.** "Shows" only for what was tested. A finding from 16 papers
   read is not a finding about 72 papers screened. Negative results are reported.
4. **Dated forecasts are never edited after the data arrive.** Write a separate evaluation.
5. **Health data only from open sources or verified access routes.** Check licence and access
   procedure first; data whose terms forbid redistribution never enter a repository.
6. **No credentials and no large raw data in version control.** Keys live in environment
   variables.
7. **One manuscript, one journal, at one time.**

## Authorship

**ICMJE — all four required for every author:** (1) substantial contribution to conception or
design, or to acquisition, analysis, or interpretation of data; (2) drafting or critically
revising for important intellectual content; (3) final approval of the version to be published;
(4) agreement to be accountable for all aspects of the work. Partial contributors go in the
Acknowledgements.

**CRediT** (14 roles: Conceptualization, Data curation, Formal analysis, Funding acquisition,
Investigation, Methodology, Project administration, Resources, Software, Supervision,
Validation, Visualization, Writing – original draft, Writing – review & editing) records *what*
each person did. CRediT does not decide who is an author — ICMJE (or the field's criteria) does.

The assistant never adds, removes, or reorders authors, and never guesses ORCIDs or emails.

## Publisher AI policies

Both major publishers agree that **AI cannot be an author** and humans are accountable for every
sentence. They differ on *where* use is disclosed:

| | Elsevier | Springer Nature |
|---|---|---|
| Where | Separate section immediately before References: *Declaration of generative AI and AI-assisted technologies in the writing process* | In **Methods** (or equivalent). Books: preface, introduction, or acknowledgements |
| Content | Tool name, purpose, extent of author oversight | Description of LLM use |
| Exempt | Basic grammar, spelling, and reference-checking tools | *AI-assisted copy editing* of human-written text for readability and grammar |
| Images | Generative AI images not permitted unless part of the research method | Similar |

If AI helped write analysis code or draft prose, disclosure is required at both. Journal-level
policies can be stricter than the publisher's, and these policies change — read the target
journal's guide for authors on the day you prepare the submission.

## Reporting guidelines

Chosen by study type, not by journal. Details and the items most often missed are in
`references/en/reporting-guidelines.md`.

- **REFORMS** (Kapoor, Narayanan et al., *Science Advances* 2024; 32 items) — any ML-based
  science. Its core concern is data leakage.
- **TRIPOD+AI** (Collins et al., *BMJ* 2024; 27 items; replaces TRIPOD 2015) — developing or
  validating a clinical prediction model, regression or ML.
- **PRISMA 2020** — systematic reviews.

## When to stop and ask

- A sentence needs a number that no results file contains.
- New results contradict a claim already written in the manuscript or abstract.
- There are signs the manuscript, or its content, is under review elsewhere.
- Any decision about authorship, author order, or conflicts of interest.
- A health-data source's licence or access route is unclear.
- The target journal's rules contradict the table above.

Say it in one or two sentences, put a placeholder in the manuscript, and continue with work that
does not depend on the answer.

## References

- `references/en/reporting-guidelines.md` — REFORMS, TRIPOD+AI, PRISMA: what reviewers catch
- `references/id/integritas-akademik-indonesia.md` — Permendikbudristek 39/2021 and textbook
  (buku ajar) requirements, in Indonesian
- `references/sources.md` — official sources for every rule, with the date checked
