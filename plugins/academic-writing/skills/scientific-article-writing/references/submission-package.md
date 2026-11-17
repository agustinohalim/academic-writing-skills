# Submission Package

## Layout

```
build_docx_<journal>.py      manuscript.md → .docx per journal rules; docstring records the rules and the date checked
Submit_<JOURNAL>/main.tex    or: the journal's LaTeX template, with \input{body} (see LaTeX below)
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

## LaTeX

Many journals take LaTeX (Elsevier `elsarticle`, Springer Nature `sn-jnl`, IEEE `IEEEtran`,
MDPI, Copernicus). Use the journal's own template, from its guide for authors or the publisher's
Overleaf gallery, never a look-alike.

```bash
python "${CLAUDE_SKILL_DIR}/../thesis-writing/scripts/ekspor_naskah.py" manuscript.md \
    --out Submit_<JOURNAL>/body --latex-body --bib refs.bib --lang en --auto-number --drop-notes
```

- `--latex-body` writes the body without a preamble; the template's `main.tex` does `\input{body}`.
- Title, authors, abstract, keywords, and highlights go into the template's own macros and
  environments; delete them from `body.tex`.
- `\cite` keys stay (natbib `\citep`/`\citet`; `--cite biblatex` if the template uses biblatex)
  and `refs.bib` is copied beside the `.tex`. Set the journal's `.bst` in `main.tex`.
- `--auto-number`: captions are written without numbers and LaTeX numbers them;
  `--drop-notes` removes the `>` editorial notes; leftover ⬜ placeholders stop the export.
- Copy the figure files into `Submit_<JOURNAL>/` with the paths `body.tex` uses.
- Compile (locally or on Overleaf) and read the PDF against the Markdown: every number, table,
  and figure. The compiled PDF is what the editor sees.

## After submission

The author presses submit, not the assistant. Then:

- Manuscript head: status note updated — date, journal, manuscript ID.
- Status board updated.
- Commit, e.g. `docs: manuscript submitted to <journal> (<ID>)`.
- The manuscript goes **nowhere else** until a decision or a formal withdrawal.
