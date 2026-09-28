# Academic English — editing journal manuscripts

The machine checker is `../../scripts/check_manuscript_en.py`.

## What the checker reports, and why

| Finding | Weight | Why it matters |
|---|---|---|
| Abstract number not found in the body | heavy | Abstracts are often written from memory of the results and drift from them |
| Citation without entry / entry never cited | heavy | Reviewers check; publishers bounce it at technical check |
| Table/figure never cited, or cited without caption | heavy | Typesetters place a table near its first citation |
| Leftover placeholders (⬜, TODO, XX) | heavy | The manuscript is not finished |
| Machine vocabulary (delve, crucial, notably, underscore, landscape, pivotal, leverage…) | light | The best-known markers to editors and reviewers |
| Repeated "X, not Y" and "rather than" | light | Forced contrast; especially visible in titles |
| Short punchline sentences ("The contrast is the paper.") | light | Rhetoric, not reporting. Short factual sentences ("No hyperparameters were tuned.") are fine |
| Em dash > 4 per 1,000 words | light | Overused stand-in for commas and colons |

## What a human must read for

**Numbers.**
- A true minus sign (−) in text, not a hyphen; ranges with an en dash (0.71–0.76).
- Consistent decimals within a metric (AUC to three places everywhere, not mixed).
- Numbers starting a sentence are spelled out; units take a space (600 dpi, 30 min) except % and °.
- One confidence-interval format throughout: "0.82 [95% CI 0.79–0.85]" or "(0.79, 0.85)".
- Report p-values, not only "p < 0.05"; leading zero per journal style.

**Tenses.**
- Methods and Results: past ("we trained", "gradient boosting ranked first").
- Established facts and what tables/figures show: present ("Table 3 shows", "ROC-AUC is
  insensitive to prevalence").
- Others' work: past for what they did, present for conclusions that still hold.

**Terminology.**
- One term per concept across the whole manuscript: "severity target" in Methods is not "fire
  threshold" in Discussion.
- Define abbreviations once in the abstract and once in the body, then use them consistently.
- "Data" plural or singular — pick one; many computer-science journals accept singular.
- One spelling variant per manuscript (British *modelling*, *favouring*, or American).

**Claims.**
- Verb strength matches evidence: *show* (tested directly) > *suggest* (consistent with) >
  *may* (conjecture). "Prove" is almost never right for empirical results.
- *Significant* only for statistical tests; for effect size say *large*, *substantial*, with the
  number.
- Avoid "novel", "first", "state-of-the-art" unless the manuscript's own review establishes it.

**Tone.** Neutral toward others' work. Critique practices, not people; drop dramatic phrasing
("impossible without anyone noticing") and dramatic section titles.

## What automated language scores measure

Services such as Research Square's language quality score (built by AJE, now offered with the
Rubriq AI editor) use a model trained on more than 100,000 papers scored by professional editors.
The score compares a manuscript's readability — grammar, consistency, **clarity** — with other
papers, so it is relative, and a mid score (5/10) means "average among submitted papers", not
"wrong". The editor's suggestion count (often hundreds) includes many stylistic rewrites.

A manuscript that is grammatical can still score in the middle, because the model rewards what
editors reward: short, well-built sentences. The features that pull a technically precise
manuscript down, and that `check_manuscript_en.py` now reports (light):

| Feature | Guide | Fix |
|---|---|---|
| Average sentence length | ≤ 22 words; < 10% over 35 words | Split at "and", ";", ", which"; one claim per sentence |
| Numbers per sentence | ≤ 2; < 10% of sentences with 4+ | Move numbers to a table; keep the one that carries the claim |
| Hyphenated noun stacks | ≤ 15 per 1,000 words | "per-district rolling-origin test folds" → "test folds that roll forward in time, with thresholds set per district" (at first use; the short form after) |
| Parentheses | ≤ 8 per 1,000 words | Promote to a sentence, or drop |
| Semicolons | ≤ 5 per 1,000 words | Two sentences |
| Punchline fragments | rare | Full sentences with a subject and verb |

Precision and readability are not in conflict: define a compact term once, then use it; keep
numbers where they prove something; let tables carry the rest.

## Errors typical of writers whose first language is Indonesian

Indonesian has no articles, no plural inflection on nouns after quantifiers, and no tense
inflection on verbs. The English errors that follow are predictable — look for them first:

| Error | Example → fix |
|---|---|
| Missing or extra article | "Model trained on panel" → "The model was trained on the panel" |
| Uncountable noun made plural | researches, informations, equipments, literatures, evidences, softwares, feedbacks, datas → studies, information, equipment, literature, evidence, software, feedback, data |
| Plural after a number missing | "three model" → "three models" |
| Tense drift inside a paragraph | Methods and Results in past tense throughout |
| Preposition calque | "discuss about", "consist from", "different with" → "discuss", "consist of", "different from" |
| Question word order | "what data we should use" in a direct question → "what data should we use?" |
| Overly long Indonesian-style sentences | Indonesian academic prose tolerates long chained clauses; English readers do not — split them |

The checker flags the uncountable plurals; articles and prepositions need a human read, ideally
aloud.

## AI copy-editing and publisher policy

AI-assisted copy editing of human-written text for readability and grammar does not need to be
declared at Springer Nature or Elsevier. If AI helped draft text or write analysis code,
disclosure is required — see the `research-integrity` skill.
