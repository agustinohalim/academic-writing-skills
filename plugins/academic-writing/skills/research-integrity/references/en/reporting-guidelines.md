# Reporting Guidelines — the items most often missed

Not a copy of the full checklists. Download the official checklist (see `../sources.md`) when
preparing a submission, fill it in, and attach it if the journal asks. This file maps the items
that most often go wrong to the manuscript section that must carry them.

## REFORMS — any ML-based study

REFORMS (32 questions in eight modules) was built from errors that recur across ML-based
science; its authors' survey found data leakage in hundreds of papers across some 30 fields.
Most relevant for time-series and spatio-temporal data:

| REFORMS module | Key question | Where in the manuscript | Typical failure |
|---|---|---|---|
| Study goals | Is the population and the claim clear? | End of Introduction | Genre drift: a methods paper that reads as a domain paper |
| Data quality | Source, period, filtering, missing data | Data | A spatial definition (bounding box vs administrative boundary) silently changes the sample |
| Preprocessing | Before or after the train/test split? | Methods | Thresholds or normalisation computed on all data instead of per fold |
| **Leakage** | Is the test set truly unseen? Split by time/group? Any feature from the future? | Methods, Validation | Positive and control windows overlap; splitting by recording while claiming "patient-level" |
| Metrics and uncertainty | Metric suited to prevalence; confidence intervals; repeats | Methods, Results | ROC-AUC alone on rare events; number of repeats in text ≠ code |
| Baselines | Is there a simple baseline (climatology, logistic regression)? | Results | Only complex models compared |
| Generalisation | Claims beyond the tested population? | Discussion, Limitations | Transfer claimed, not tested |
| Reproducibility | Code, versions, seeds, derived data | Code/Data availability | Code released without the version that produced the numbers |

**Three questions to ask of every result before writing it down:**

1. Did any information from the test data — normalisation statistics, thresholds, feature
   selection, hyperparameter choice — influence the model?
2. Is the unit of splitting (patient, recording, district, year) the same unit the text claims?
3. Does the number in the text match the log, including number of repeats and sample size?

An AUC far below 0.5 almost always means an inverted label, not a strong negative signal.

## TRIPOD+AI — clinical prediction models

27 items plus a separate TRIPOD+AI for Abstracts checklist. Applies to regression and ML alike.
Items most often incomplete:

| Item | Content | Watch for |
|---|---|---|
| Title/abstract | State development and/or validation, population, outcome | Use the Abstracts checklist |
| Data sources | Databases, period, recording method | List **every** database in Data availability |
| Participants | Inclusion criteria; number of patients **and** of recordings | Recordings ≠ patients |
| Outcome | Definition and timing | Prediction horizon and window definitions |
| Predictors | How measured; automatic vs audited annotation | Different annotation processes between classes are a confounder |
| Sample size | Justification | Say plainly if limited by open data |
| Analysis | Data splitting, class imbalance, calibration | |
| Fairness | Performance by subgroup where relevant | Age/sex when available |
| Limitations | Including risk of bias and applicability | |

Its companion risk-of-bias tool, PROBAST+AI, applies when a paper appraises other people's models.

## PRISMA 2020 — systematic reviews

A flow diagram is required: identified → screened → full text assessed → included, with the
**same numbers** in the abstract, body, and any README or supplement. Write the flow once and
reuse it everywhere.
