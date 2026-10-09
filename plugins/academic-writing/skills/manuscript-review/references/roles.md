# Review Roles

Five roles, each with a job the others do not do. Every role scores all seven dimensions (1–5)
but writes findings mainly about its own area. Roles do not read each other's output.

## editor — journal fit and contribution

The editor decides whether the paper deserves reviewers' time.

- State the central contribution in one sentence. If it cannot be done without a place or
  dataset name, or needs "and", that is a finding (`originality` or `significance`).
- Is it new relative to the closest prior work the paper itself cites? Confirmation of a known
  effect in a new setting is not novelty.
- Would readers of the target journal outside this region/dataset change what they do?
- Does the title state the finding? Does the abstract build one arc?
- Is the paper's genre clear (finding, method, benchmark, negative result)? Does it follow that
  genre's skeleton (`scientific-article-writing/references/genre-patterns.md`): a named resource
  with a repeated fingerprint for a benchmark; numbered, citable prescriptions for an
  evaluation critique; named checks for a confound paper?
- Compliance screen: required declarations present (competing interests, funding, data
  availability, ethics, AI statement where the publisher puts it); length and structure as the
  target journal asks.
- Target-journal fit, when the panel note names one: an aims-and-scope sentence that fits, and
  resemblance to its recent papers. Indexing status is out of scope for reviewers
  (`journal-targeting`).
- Desk-reject test: what would make an editor stop at page one?

## methods — design, statistics, reproducibility

The methods reviewer decides whether the numbers can be trusted.

- Does the design answer the question: baselines, controls, right unit of analysis?
- Leakage: anything from test data in training, normalisation, thresholds, feature or model
  selection? Split by the unit the claims are about (patient vs recording, region vs pixel,
  year)?
- Uncertainty for every comparison that carries a claim; number of repeats stated and
  consistent.
- Metrics suited to the question and prevalence; calibration when probabilities are used.
- Robustness checks that could change a conclusion: in the main text or only in Limitations?
- Reproducibility: code, data, versions, seeds.
- The decisive contrast: are the same models scored under the standard and the honest
  evaluation, with only the evaluation changed? Is there a cheapest competitor (climatology,
  persistence, prevalence only, one nuisance feature)? For a probe or confound check, a null
  control (permuted labels, surrogate) showing the probe does not score high on arbitrary labels?
- Use `third-party/k-dense/common-review-issues.md` and `statistical-reproducibility-review.md`,
  and REFORMS / TRIPOD+AI where they apply.

## domain — literature and positioning

The domain reviewer decides whether it is new and correctly placed.

- Is the related work organised by idea, and does each group end with the paper's position?
- Is the gap supported by evidence, not asserted? Strongest forms: a comparison table with the
  new resource or tool in the last row, a coded count of how prior studies did it (with an
  *Unclear* class), a degenerate example the usual metric rewards. "No study has…" alone is a
  finding.
- Tone toward prior work: is a critique shown on the authors' own models, or does a sentence
  name other authors as wrong? The latter invites hostile reviewers; flag it under `argument`.
- Are closely related lines of work missing? **Describe the kind of work** ("studies of label
  shift under regional base-rate differences"), never invent an author or title.
- Are established results presented as contributions?
- Are domain facts (processes, drivers, data products) stated correctly and with sources?

## presentation — structure and readability

The presentation reviewer decides whether a reader can follow it.

- One central message carried through title, abstract, introduction, results headings,
  conclusion?
- Introduction: territory → gap (cited) → what this paper does.
- Results: subsections as claims; each paragraph question → evidence → answer; no new results in
  the Discussion.
- Zig-zag: the same subject treated in several places; alternating between settings.
- Sentence level: long sentences, number-dense sentences, noun stacks, undefined abbreviations —
  use the machine findings in `machine.json` as leads, and quote the worst instances.
- Figures and tables: cited in order, readable alone, titles state conclusions.
- Does Figure 1 show the mechanism, design, or data pipeline before any result? Is the organising
  axis of Results announced (by check, by finding, by benchmark)? Are prescriptions numbered and
  restated in the Discussion or Conclusion?

## devils-advocate — the strongest objection

The devil's advocate tries to make the main claim fall.

- Write `strongest_counterargument`: the single best argument that the main conclusion is wrong
  or much narrower than stated.
- Overgeneralisation: how many settings, units, or years carry the general claim?
- Alternative explanations the paper does not rule out (confounders, artefacts of data
  processing, selection).
- Cherry-picking: results reported for some settings or thresholds but not others.
- The "so what" test: if everything is true, what changes for anyone?
- For a critique or confound paper: does any case pass? If every benchmark or study fails, the
  check may be too strict; ask for a case that passes or a dose-response showing when the
  problem appears.
- Is there a fence sentence (what the finding is *not*) in the abstract, sized to the headline
  number?
- Severity is honest: a counter-argument the paper already addresses adequately is `minor` or
  not a finding.
