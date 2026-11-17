# Changelog

All notable changes to the `academic-writing` plugin. The version is the one in
`plugins/academic-writing/.claude-plugin/plugin.json`. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow semantic versioning.

No git tags exist for versions up to 1.12.0. They were reconstructed from the commit history and
the version bumps in `plugin.json`. From the next release on, each version is tagged `vX.Y.Z`,
which `install.py update --ref vX.Y.Z` can install.

## [1.13.0] — 2026-11-17

### Added
- `thesis-writing` skill: drafts skripsi, tesis, and disertasi chapters (Bab I–V) from the
  author's own material, with quantitative, qualitative, mixed-methods, and R&D paths, and
  `ekspor_naskah.py` to export the chapters to DOCX and PDF in the campus format.
- `research-integrity/scripts/verify_references.py`: checks a reference list against Crossref
  and OpenAlex (DOI resolves, DOI belongs to the cited paper, unlisted works found by
  bibliographic search) and gives Garuda and SINTA pointers for Indonesian sources that need a
  manual check.
- `install.py`: installs the skills for Codex, Gemini CLI, OpenCode (`~/.agents/skills`), or
  any other agent's skills folder. Commands: `install`, `version`, `check-update`, `update`
  (with a backup first), `rollback`, `uninstall`. Python standard library only.
- This changelog.

## [1.12.0] — 2026-11-11

### Changed
- `scientific-article-writing`, `journal-targeting`: the journal is chosen after the drafted
  body (stage 4c). Methods, Results, and Discussion come first, then scorecard section A, then
  the ladder for the contribution the results carry, then Introduction, Abstract, and Title.

## [1.11.1] — 2026-11-02

### Fixed
- `manuscript-proofreading`: in-text citations with a diacritic initial ("Åkesson et al.,
  2024") are matched to their reference entry, so they are no longer reported as uncited.

## [1.11.0] — 2026-10-29 to 2026-11-02

### Added
- `scientific-article-writing/references/gap-from-limitations.md`: find the gap in the closest
  papers' own limitations, and show the problem is still open before claiming it.

### Changed
- Stage 1 is "gap, then plan". The paper must add a finding, method, resource, or decision the
  reader did not have. Scorecard A2 and A8 are scored at stage 1.
- README: workflow flowchart in both languages (`docs/article-workflow.svg`).

## [1.10.0] — 2026-10-16

### Added
- `manuscript-review`: submission readiness gate, separate from the decision (no Reject,
  editor desk verdict `send_to_review`, median significance and originality ≥ 3,
  `journal_fit.md` present, no heavy machine finding, all five roles run).
- `prepare_review.py --fit` copies the target journal's fit evidence into the workspace.
  `diff_review.py` shows readiness before and after a revision.

### Changed
- `journal-targeting`: no same-day resubmission, and transfers get the full fit test. Two
  editorial rejections in a row take the paper off the ladder.

## [1.9.2] — 2026-10-10

### Changed
- `journal-targeting`: index status is checked in Web of Science (Master Journal List, holds)
  and in the publisher's own notices, not only in Scopus.

## [1.9.1] — 2026-10-09

### Changed
- `journal-targeting`: notes from the first real ladder. The Scopus monthly source list covers
  every rung, Scimago can lag on open-access status, and fit is measured with per-journal
  PubMed counts.

## [1.9.0] — 2026-10-09

### Added
- `journal-targeting` skill: a ladder of three or four journals, fit tested against recent
  papers, index status verified on the day of submission, hijacked and predatory journals ruled
  out, metrics explained, and what to do after rejection or a transfer offer.
- Review roles: compliance screen and target-journal fit check.

## [1.8.0] — 2026-10-07

### Added
- `scientific-article-writing/references/genre-patterns.md`: patterns from 34 accepted papers.
- `check_manuscript_en.py`: three light checks (gap asserted without a citation, critique that
  names authors as wrong, "significant" without a test). Review roles and scorecard check the
  genre skeleton.

## [1.7.0] — 2026-10-06

### Added
- `scientific-article-writing/references/editor-and-reviewer-criteria.md`: desk screen and
  reviewer criteria from Elsevier and Springer Nature, journal exclusion lists, and the "solves
  nothing" trap. Scorecard A8 (does the paper let the reader do something new?).

## [1.6.1] — 2026-09-28

### Fixed
- `thesis-audit`: parser handles forms found in a real 2022 thesis ("Surname, et al. Year",
  "Rumusan Permasalahan", lower-case "pada tabel 4.1", 96.67 vs 96,67). New check for caption
  numbers used twice. Guidance for PDF-only theses.

## [1.6.0] — 2026-09-28

### Added
- `thesis-audit` skill: audits a skripsi, tesis, or disertasi as one research chain.
  `prepare_audit.py` runs mechanical checks, the model judges fourteen modules, and
  `report_audit.py` verifies quotes, enforces status and severity rules, and writes the
  supervisor report and student feedback.

## [1.5.0] — 2026-09-28

### Added
- `manuscript-review`: `impact_review.py` (revision impact: values changed in one place but left
  in another, sections edited and not edited) and a `not_assessable` state for questions the
  manuscript gives no material to answer.

## [1.4.1] — 2026-09-28

### Fixed
- `consolidate_review.py`: optional `merges.json` for the same issue raised at different places.
- `check_manuscript_en.py`: "Table 7 of Smith et al. (2014)" is no longer a missing table.

## [1.4.0] — 2026-09-28

### Added
- `manuscript-review` skill: simulated peer review by five independent roles, shipped as plugin
  agents, with quote verification, consensus, scorecard, decision rules, and a re-review diff.
- Unit tests and a GitHub Actions workflow.

### Fixed
- `manuscript-proofreading`: the description was not valid YAML, so the skill had loaded
  without metadata since 1.2.0.

## [1.3.0] — 2026-09-28

### Added
- Two review checklists from K-Dense scientific-agent-skills (MIT, attributed), an
  overstatement check, and tested verdicts on three related skill collections.

## [1.2.0] — 2026-09-28

### Added
- `manuscript-proofreading`: LanguageTool wrapper (`check_grammar_lt.py`), patterns derived from
  blader/humanizer, and a survey of related tools.

## [1.1.0] — 2026-09-28

### Added
- `scientific-article-writing`: story and structure guidance and a pre-submission scorecard.
- `manuscript-proofreading`: light checks for sentence length, number density, noun stacks, long
  abstracts, and new numbers in the Discussion. Notes on errors typical of Indonesian-L1 writers.

## [1.0.0] — 2026-09-28

### Added
- Marketplace and plugin manifests, bilingual README, dual licence (MIT for scripts, CC BY 4.0
  for the rest).
- `research-integrity`, `manuscript-proofreading` (English and Indonesian checkers), and
  `scientific-article-writing` (gated journal-article workflow).
