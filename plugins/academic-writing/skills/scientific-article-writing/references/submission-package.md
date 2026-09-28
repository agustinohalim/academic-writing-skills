# Submission Package

## Layout

```
build_docx_<journal>.py      manuscript.md → .docx per journal rules; docstring records the rules and the date checked
Submit_<JOURNAL>/            upload-ready files (manuscript, figures, cover letter, highlights)
Submission_<JOURNAL>.md      every portal text, ready to copy-paste; notes to the author clearly marked
```

## Contents of Submission_<JOURNAL>.md

1. **Cover letter** — one page: title, the problem, what was found (one or two numbers), why it
   fits this journal's readers, a statement that it is not under consideration elsewhere, on
   behalf of all authors. No date line (the portal stamps it).
2. **Statements** — competing interests, funding, CRediT, data availability, AI.
3. **Suggested reviewers** — name, verified affiliation (e.g. via OpenAlex), why suitable.
   **Never invent email addresses**; take them from the reviewer's papers or institution page,
   or leave a placeholder. List whom to avoid and why (authors criticised in the paper, same
   institution, co-authors' institutions).
4. **Already in the manuscript** — so nothing is entered twice in the portal.
5. **Before pressing submit** — table of upload files and their state; table of checks
   (references verified, overlap check, code with DOI, declarations complete, **written approval
   from every co-author**).

## Journal rules

Read the journal's submission guidelines on the day of packaging and summarise them in the
builder's docstring with the date. Always check: abstract word limit, keyword count, highlights
(Elsevier), figure format and resolution, reference style, single- or double-blind review
(separate title page?), where the AI statement goes.

## After submission

The author presses submit, not the assistant. Then:

- Manuscript head: status note updated — date, journal, manuscript ID.
- Status board updated.
- Commit, e.g. `docs: manuscript submitted to <journal> (<ID>)`.
- The manuscript goes **nowhere else** until a decision or a formal withdrawal.
