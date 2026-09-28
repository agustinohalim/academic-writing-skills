# Pre-Submission Scorecard

Score the manuscript the way independent pre-review services and editors do, **before**
submitting. Modelled on the three dimensions of the Rubriq peer-review scorecard (R-Score) — quality of research,
quality of presentation, novelty and interest.

The key fact about that model: **novelty and interest set the range of the overall score; quality
only moves the score within that range.** A flawless paper whose contribution reads as local or
incremental cannot score high. Polishing language raises a 5 to at most a 6; reframing the
contribution is what moves the range. Work on section A first.

Score each question 0 (no), 1 (partly), 2 (yes). Write one line of evidence per score — a
score without evidence is not a score.

## A. Novelty and interest — sets the range

| # | Question | Evidence |
|---|---|---|
| A1 | Can the central contribution be stated in one sentence (≤ 30 words) without a place or dataset name? | |
| A2 | Is that contribution new relative to the closest prior work (named, cited), not a confirmation of a known effect? | |
| A3 | Would a reader working on a *different* region, dataset, or population change what they do after reading? | |
| A4 | Does the title state the general finding (not "evidence from <place>" / "a case study of")? | |
| A5 | Does the first paragraph of the Introduction make a non-specialist in the journal's readership care? | |
| A6 | Is the contribution type stated positively (finding, method, benchmark, negative result with mechanism), without apologising for what it is not? | |
| A7 | Is the claim's scope earned (more than one setting, or scope stated precisely)? | |

## B. Quality of research — position within the range

| # | Question | Evidence |
|---|---|---|
| B1 | Is the design able to answer the question (controls, baselines, splits by the right unit)? | |
| B2 | Leakage ruled out (REFORMS questions)? | |
| B3 | Uncertainty reported for every comparison that carries a claim? | |
| B4 | Robustness checks that could change the conclusion are in the main text, not only in Limitations? | |
| B5 | Sample size / number of settings adequate for the generality claimed? | |
| B6 | Code and data available, version named? | |

## C. Quality of presentation — position within the range

| # | Question | Evidence |
|---|---|---|
| C1 | Abstract is one arc (context → gap → action → result → meaning) with ≤ 4 numbers? | |
| C2 | Introduction follows CARS, with the gap evidenced by citation? | |
| C3 | Contribution list ≤ 4 items, each distinct from prior work? | |
| C4 | Results subsections are claims, each paragraph question → evidence → answer? | |
| C5 | No new results in the Discussion; Discussion says how the gap was filled? | |
| C6 | No zig-zag: each subject treated in one place; one setting at a time? | |
| C7 | Figures readable alone; titles state conclusions? | |
| C8 | Language clean (`check_manuscript_en.py` heavy = 0; light findings read)? | |

## Reading the result

- Section **A below 10 of 14**: the paper will be read as incremental or local. Do not submit yet;
  revise title, abstract, introduction, and contribution list first (see `story-and-structure.md`).
- B or C weak with A strong: fixable in revision; submit to a journal whose readership matches A3.
- Write the scorecard into the self-review file with the date, so a later external score can be
  compared against it.

## Using an external score

First establish **what** the score measures:

- **An automated language score** (e.g. Research Square's language quality score with the Rubriq
  AI editor) measures readability only — grammar, consistency, clarity — relative to other
  papers. Treat it with `manuscript-proofreading` (sentence length, number density, noun stacks,
  articles), not by reframing the paper. It says nothing about novelty.
- **A peer-review scorecard** (Rubriq's original three-reviewer R-Score, a colleague's review, a
  desk rejection) judges the science. Map each comment to the questions above before changing
  text. Mid scores of this kind usually trace to A1–A4, and polishing language will not move them.
