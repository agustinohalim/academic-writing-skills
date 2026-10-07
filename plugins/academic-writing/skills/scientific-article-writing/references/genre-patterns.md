# Genre Patterns: How Accepted Papers of Each Kind Are Built

Distilled in October 2026 from a structural reading of 34 published papers in four genres that
methodology-minded ML papers usually fall into: dataset/benchmark papers, papers that reform an
evaluation practice, leakage/shortcut/confound papers, and method-plus-software papers in
biomedical-engineering venues. The point is how they are *written and argued*, not whether their
science is right. Use this file at stage 1 (choose the genre and its skeleton) and stage 3 (outline),
and again in the self-review.

Pick the genre first; the venue then decides the headings, but not the spine.

## 1. The spine shared by all four genres

1. **Stakes tied to a decision.** The model's output feeds a decision (preparedness, referral,
   early warning, carbon accounting), so a wrong evaluation is a wrong decision. Say this before
   any method.
2. **Concede, then pivot.** Grant the practice under criticism its legitimate use before naming the
   assumption it silently relies on ("While essential in monitoring training…", "There are good
   reasons for combining cohorts…"). A reader who feels their practice was described fairly keeps
   reading.
3. **Evidence the gap; never only assert it.** One of: a comparison table whose last row is your
   resource; a coded count of prior studies ("17 of 63"), with an *Unclear* class as the benefit of
   the doubt; a degenerate model the usual metric rewards; a paradox in the published record.
   "No study has…" on its own is the weakest form and the one reviewers challenge first.
4. **Mechanism before measurement.** Explain *why* the practice misleads — prose, an equation, or
   Figure 1 — before the results, so the results read as confirmation rather than surprise.
5. **Same models, two evaluations.** Hold the pipeline fixed, change only the evaluation (split
   unit, threshold, pooling, metric) and report the collapse or the rank reversal side by side.
   This is the single strongest evidence move in every genre.
6. **The cheapest competitor.** Climatology, persistence, one index, prevalence only, one nuisance
   feature. If it matches the sophisticated model, the argument no longer depends on which
   evaluation is "right".
7. **A citable device.** Numbered guidelines, named checks, a coded taxonomy, a two-condition rule —
   restated compactly in the Discussion or Conclusion so others can cite "Guideline 3" or "check 2".
8. **A fence on the claim.** Say what the finding is *not* ("dataset membership, not causal site
   effects"; "a lower bound"). The larger the headline number, the tighter the fence; put one
   fence sentence in the abstract.

### Blame the procedure, not the people

What it means in practice: **show the error with your own models, not by marking down other
authors.**

- Rebuild the field's standard pipeline yourself — a published architecture "without
  modification", the usual random split, a balanced test set.
- Run your own model through it, then through the honest evaluation, and report that *your* model
  looked good under the first and failed under the second.
- Attribute the cause to the procedure ("an undisclosed protocol choice", "procedures often used",
  data scarcity), and cite prior studies as instances of a pattern, in batches, not as defendants
  in a verdict sentence.

Why it works: nobody is accused, so reviewers who wrote those papers have nothing to defend; and the
rebuttal "you implemented our method badly" is closed, because the demonstration does not depend on
anyone else's implementation. A combative framing can still be published but tends to draw reply
papers instead of uptake.

Wrong: "Author A (2020) and Author B (2012) leaked patients between folds, so their accuracies are
invalid." Right: "Under a split by series pair, as is common for this database, our model
reaches 0.71; under a split by patient the same model reaches 0.68." Then, in Related work, a coded
table of how prior studies split, with an *Unclear* column.

## 2. Dataset and benchmark papers

- **Title:** `Name: a [qualifier] dataset/benchmark for [task] in [place]`. A coined name before a
  colon makes the resource citable; dataset titles rarely state a finding.
- **Fingerprint repeated verbatim** in abstract, Introduction and Data: variables × spatial
  resolution × temporal resolution × period × samples.
- **One-sentence reason for every design parameter** (cell size, time step, negative ratio, buffer),
  with a precedent citation where one exists.
- **Data before models:** a construction pipeline or sample gallery as Figure 1–2. A map suits
  place-anchored work but does not replace the pipeline.
- **Gap as a comparison table**, new resource in the last row, columns for the dimensions you win on.
- **Report where it fails:** a hard test set, strata where the method does not beat the baseline,
  a named event with visible errors. Plain reporting of failure reads as more credible than
  promotional adjectives.
- **A release package, not a promise:** data DOI, code repository, version, licence, and for data
  venues a datasheet or usage notes. "Available on reasonable request" is a weakness reviewers note.
- Uncertainty is rare in this genre (few CIs, few seeds); providing it is a cheap way to stand out.

## 3. Papers that reform an evaluation practice

- **A degenerate model the standard metric prefers**, shown in one small example before any data
  (a "never fire" model with the best MAE; "everyone low risk" at 99 % accuracy).
- **A ladder of trivial baselines** so the claim survives whichever evaluation the reader prefers.
- **Translate each metric into an action** a manager, clinician or forecaster would take
  differently.
- **Reframe a binary debate as a continuum** on which both sides are right somewhere (degree of
  extrapolation; imbalance → calibration).
- **Numbered prescriptions**, restated later. Title forms that pass: a claim with an active verb,
  a harm claim ("The harm of…"), a genre promise ("Guidelines for…"), or a question.

## 4. Leakage, shortcut and confound papers

- **Predict the nuisance variable directly** (hospital, cohort, source database) and report how far
  above chance it lands.
- **A null for the null:** permutation of labels, surrogates or random initialisation, to show the
  probe does not produce high scores for arbitrary labels.
- **Dose-response or 2×2** showing *when* the confound bites (easy/hard target × balanced/imbalanced
  prevalence), which answers "so is every benchmark confounded?". Showing at least one benchmark
  that passes serves the same purpose.
- **State scepticism against yourself up front** ("a priori we consider X unlikely to carry…"); a
  positive result then reads as discovered, not advocated.
- **Announce the organising axis of Results** ("organised by check, not by dataset").
- **Verdicts as stopping points of a claim** ("the claim of a pre-event signal stops at the horizon
  check"), not as grades on earlier papers. PASS/FAIL may stay in the software output.

## 5. Biomedical-engineering venues (CMPB, CBM, TBME house style)

- **Structured abstract as a mini-paper:** gap in Background; datasets, split unit (patient-wise)
  and evaluation design in Methods; numbers in Results; a trade-off or scope fence in Conclusions.
- **State the split in the abstract and draw it.** Report the leaky protocol next to the correct
  one and give the gap as a result.
- **Gap as a feature/limitation matrix of prior tools**, not an absence claim.
- **Comparison with prior work recomputed on a common subset** of records where possible.
- **Discussion split into named subsections:** comparison with other work, limitations (numbered),
  future work.
- **Software availability is part of Methods:** repository with the scripts that produce every
  number, licence, hardware, library versions, measured run time. Highlights: 3–5 noun-phrase
  bullets, the first with a number.

## 6. Slips seen in published papers

Cheap to prevent, costly at review: placeholders left in ("see XX"); a caption citing an RQ that
does not exist; a year range that differs between Methods and Results; absolute differences on a
0–1 scale written as percentages; "significantly" without a test; numbers that differ between
sections; a reference that does not support the sentence it is attached to. Machine checks catch
most of these; run them.

## Exemplars

Dataset/benchmark: Kondylatos et al. 2023 (Mesogeos, NeurIPS D&B); Karasante et al. 2025 (SeasFire
cube, *Scientific Data*); Huot et al. 2022 (Next Day Wildfire Spread, *IEEE TGRS*); Porta et al. 2026
(CanadaFireSat, *ISPRS J*); Nikonovas et al. 2022 (ProbFire, *NHESS*).
Evaluation practice: Phelps & Woolford 2021 (*Int J Wildland Fire*); Ploton et al. 2020 (*Nat Commun*);
van den Goorbergh et al. 2022 (*JAMIA*); Linnenbrink et al. 2026 (arXiv); Roberts et al. 2017
(*Ecography*).
Leakage/confound: Kapoor & Narayanan 2023 (*Patterns*); Zech et al. 2018 (*PLOS Med*); Geirhos et al.
2020 (*Nat Mach Intell*); Brookshire et al. 2024 (*Front Neurosci*); Mørch-Pedersen et al. 2026
(*BSPC*); Zare 2026 (arXiv).
Biomedical engineering: de Chazal et al. 2004 (*IEEE TBME*); Moody et al. 2001 (*Computers in
Cardiology*); Santamónica et al. 2024 (ECGMiner, *CMPB*).
