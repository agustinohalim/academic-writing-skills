# Modules

Fourteen modules, ordered along the research chain. Each answers one question. Read the whole
thesis once before starting; then answer module by module, writing findings as you go.

A module ends in exactly one status:

| Status | When |
|---|---|
| `found` | at least one concrete problem, quoted |
| `not_found` | the module's question could be answered from the text and no problem turned up |
| `not_assessable` | the question cannot be answered because an input is absent — name it in `missing` |
| `not_applicable` | the question does not arise for this kind of study — say why in `basis` |

`not_found` is not "clean everywhere"; `not_assessable` is not a pass. The report shows both.

## Research types change what "correct" means

Name the type in `research_type` before judging. Most S1 theses in computing programmes are one
of these:

| Type | Chain to trace | Where it usually breaks |
|---|---|---|
| `system-development` (rancang bangun, sistem informasi, aplikasi) | problem at the site → requirements → design (UML/ERD) → implementation → testing of each requirement → conclusion | requirements never tested; black-box table tests screens, not requirements; "sistem berhasil" with no acceptance criterion; UAT on a handful of people read as general acceptance |
| `quantitative` (survey, TAM/UTAUT, PLS-SEM, regression) | theory → hypotheses → constructs → indicators → sample → validity/reliability → test → conclusion | hypotheses not drawn from the cited theory; sample size unjustified; causal wording from a cross-sectional survey; significance read as effect size |
| `ml` (data mining, klasifikasi, prediksi, deep learning) | question → dataset → split → baseline → metric → result → claim | leakage (preprocessing or oversampling before the split; same subject in train and test); accuracy on imbalanced data; no baseline; one run, no variance; claims beyond the dataset |
| `qualitative` (wawancara, studi kasus) | question → informants → data collection → coding → themes → conclusion | informant selection unexplained; themes asserted without quoted evidence; generalising from a case |
| `review` (SLR, bibliometric) | question → search string → databases → inclusion/exclusion → screening counts → synthesis | search not reproducible; PRISMA counts that do not add up |
| `mixed` / `by-publication` | as above per part, plus how the parts connect | parts that do not answer a shared question |

## The modules

**M01 Structure and completeness.** Are the parts the level requires present and in order
(abstract, introduction with problem statement and objectives, literature, method, results and
discussion, conclusion, references; appendices the method promises — instrument, test
scenarios, code)? Missing parts that the method depends on are findings; a different heading
name is not. Faculty templates vary; if a template is supplied, it outranks this list.

**M02 Problem - objective - conclusion chain.** The spine. Put `chain.json` side by side: every
rumusan masalah needs an objective that addresses it and a conclusion that answers it, in the
same terms. Look for: an objective with no question; a question answered nowhere; a conclusion
that answers a different question ("bagaimana merancang" answered with "sistem berhasil
dirancang" says nothing about how); objectives that promise evaluation the method never does.
Counts that differ are flagged by the machine; judge whether the mismatch is real (one
objective legitimately covering two questions is fine if it says so).

**M03 Background and gap evidence.** Is the problem shown to exist — at the site, in data, in
prior work — or only asserted? Is the gap evidenced by what prior studies did not do, or by
"belum ada penelitian" with no search behind it? For system-development theses: is the
existing process described concretely enough that the new system's improvement can be judged?

**M04 Literature and theory.** Does the literature synthesise (compare, contrast, show what is
unresolved) or list one study per paragraph? Is the theory actually used later — hypotheses
drawn from it, constructs measured as it defines them — or only described? Are sources suitable
(primary, recent where recency matters; textbooks for definitions are fine)?

**M05 Method fits the questions.** Can this design answer each question? A causal question
needs a design that can support it. A "how effective" question needs a comparison or a
criterion. Development method (waterfall, prototype, RAD, agile) should match how the work was
actually done; a method chapter that describes a textbook method no one followed is a finding.

**M06 Constructs, variables, requirements.** Is every key term defined once and used the same
way? Quantitative: does each indicator measure its construct, and is the instrument attached?
System development: are requirements specific enough to test ("sistem mudah digunakan" is not)?
ML: are the target label and features defined operationally?

**M07 Data, sample, and numbers.** Do N, counts, and totals agree across method, tables, and
text? Are exclusions explained? Do table rows sum? Does the sample or dataset support the
population the conclusions talk about? Do reported percentages match their counts?

**M08 Analysis, testing, and interpretation.** Are tests appropriate and their assumptions
checked where it matters? Are p-values, effect sizes, metrics read correctly? Black-box testing:
does it test requirements, including invalid input, or only happy paths? UAT/SUS: is the score
computed correctly and interpreted against its scale? ML: is the metric right for the class
balance, is there a baseline, is variance reported?

**M09 Claims sized to evidence.** Does any sentence in the discussion, conclusion, or abstract
claim more than the results show — causation from association, generality from one site,
"meningkatkan efisiensi" with no before/after measure? Quote the claim; point to what the
evidence actually supports.

**M10 Consistency across chapters.** Same numbers, names, sample, method, and scope in every
chapter? A variable renamed, a sample that changes size, a method in chapter III that differs
from what chapter IV reports?

**M11 Citations and references.** Machine findings cover missing and unused entries. Judge the
rest: do cited sources support the sentence they are attached to (only where you can see the
source)? Secondary citation passed off as primary? Reference style consistent? Never invent a
reference to fill a gap; describe what kind of source is missing.

**M12 Integrity risks.** Only on evidence: text that a supplied source matches closely; data
that looks too clean to be real (identical rows, impossible values, perfect results on small
samples); figures reused from elsewhere without credit. **Never judge AI authorship or
plagiarism from style alone** — if it matters, name what evidence would settle it (source text,
Turnitin report, drafts, data files) and mark the module `not_assessable`.

**M13 Contribution and originality.** Can the contribution be stated in one sentence, and is it
what the conclusion delivers? For S1 the bar is correct and complete work on a real problem,
not novelty; do not penalise a skripsi for not being new. For tesis and disertasi, ask what is
known after this work that was not known before.

**M14 Dissertation thread and publications** (disertasi only). See `dissertation.md`.

## Severity and evidence

| Severity | Consequence | Needs |
|---|---|---|
| `critical` | a main conclusion may be wrong or unsupported; examiners would not pass it as is | `status: confirmed` and `confidence: high` |
| `major` | an examiner will certainly require it | `confirmed` or `likely` |
| `minor` | improves the thesis | anything, including `potential` |

Before writing `critical` or `major`, look for the innocent explanation (the number is
explained in a footnote; the term is defined in an appendix). The script refuses a `critical`
that is not confirmed with high confidence: that is deliberate, because a supervisor's "this is
fatal" to a student has to be right.

A preference is not a finding. Style, word choice, and layout belong to proofreading
(`manuscript-proofreading`), not here.
