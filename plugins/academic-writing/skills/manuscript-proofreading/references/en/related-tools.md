# Related Tools

Surveyed 28 September 2026 on GitHub. Stars and licences as of that date. What each is good for,
and where it conflicts with research-writing conventions.

## Deterministic checkers (no LLM; reproducible)

| Tool | Licence | Catches | Notes |
|---|---|---|---|
| [LanguageTool](https://github.com/languagetool-org/languagetool) via `language_tool_python` | LGPL-2.1 | Grammar, agreement, confused words, spelling; 25+ languages | Local with Java 17+. Wrapped here as `scripts/check_grammar_lt.py`. On a machine-drafted manuscript it typically finds almost nothing — a mid automated language score is then about readability, not grammar |
| [proselint](https://github.com/amperser/proselint) | BSD-3 | Clichés, weasel words, redundancy, typography | Few hits on technical prose |
| [write-good](https://github.com/btford/write-good) | MIT | Passive voice, weasel words, "there is" openers | Flags every passive — too strict for Methods |
| [Vale](https://vale.sh) + [vale-ai-tells](https://github.com/tbhb/vale-ai-tells), [vale-llm-slop](https://github.com/Syntaf/vale-llm-slop) | MIT | Configurable style rules; packages for AI tells | Best if a team wants one rule set in CI |
| [textlint](https://github.com/textlint/textlint) + [slopless](https://github.com/berelevant-ai/slopless) | MIT | Deterministic "prose slop" rules for English Markdown | Node-based |
| [TeXtidote](https://github.com/sylvainhalle/textidote) | GPL-3 | LaTeX-aware grammar via LanguageTool | For `.tex` sources |

## Agent skills (LLM guidance)

| Skill | Licence | Use it for | Caveat |
|---|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | MIT | 26-pattern taxonomy of AI-writing tells (staged contrasts, forced triads, hyphenated pairs, -ing riders, copula avoidance…) | The -ing rider, copula, and hedge patterns are included in `check_manuscript_en.py`. Rewrites must not add facts — the skill says so too |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | MIT | Short rule set and a 5-dimension score | "No passive, no adverbs, no em dashes, put the reader in the room" suits essays, not Methods sections; do not apply wholesale to a manuscript |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) (`scientific-writing`, `peer-review`) | MIT | Evidence provenance, claim–evidence audit, reporting-guideline selection, structured peer review with scripts | Overlaps `scientific-article-writing` and `research-integrity`; installing both makes two skills fire for one task |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (`academic-paper-reviewer`) | CC BY-NC 4.0 | Simulated five-seat review panel including a journal-fit reviewer and a devil's advocate — useful for the novelty/framing questions a language score does not touch | Non-commercial licence |
| [bahayonghang/academic-writing-skills](https://github.com/bahayonghang/academic-writing-skills) | none stated | LaTeX/Typst paper audit, grammar and de-AI polish, cover-letter alignment | No licence: use, don't copy |
| [wanshuiyin/Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch) | MIT | Reviewer-side integrity forensics (self-consistency of numbers, claims) | Aimed at AI-generated papers |

## What none of them do

No open tool reproduces a commercial language score such as Research Square's; those models are
trained on proprietary editor ratings. The measurable proxies — sentence length, number density,
noun stacks, punctuation load — are what `check_manuscript_en.py` reports, and they move the
score. Grammar tools catch errors; they do not make a dense paragraph readable.
