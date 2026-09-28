# Story and Structure

A manuscript can be correct, well-reported, and grammatical and still score in the middle,
because reviewers judge **what the paper is about** before they judge how well it is done. This
file collects the structural rules that decide that first judgement.

## 1. One central contribution

> "Readers can still describe the main contribution of your paper to their colleagues a year
> after reading it." — Mensh & Kording (2017), rule 1

Test before writing anything else: **state the contribution in one sentence of ≤ 30 words, with
no place name and no dataset name in it.** If that is impossible, the paper has more than one
message or its message is local.

Symptoms of a paper with several messages:
- the title contains two claims joined by "and";
- the contribution list has more than three or four items of equal weight;
- the abstract lists findings instead of building to one;
- Results alternate between two settings (one region, then many; one dataset, then another).

A merged manuscript (two planned papers combined) almost always shows all four. Decide which
finding is the paper and demote the rest to supporting evidence, or split again.

## 2. Frame the general question; the site is the evidence

Reviewers ask "who outside this region, dataset, or population cares?" A title ending in
"evidence from <place>" or "a case study of <place>" tells them the answer is "few". Put the
general question in the title and first paragraph; the place appears as the test bed.

| Local framing (reads as a case study) | General framing (reads as a finding) |
|---|---|
| Comparing flood-forecast models: evidence from province P | How the label definition decides whether ML evaluation conclusions transfer between regions |
| Deep learning for X in hospital Y | When does a model validated in one hospital fail in another, and why |

The general claim must be earned: if it rests on one island or one hospital, either add a second
setting or state the scope precisely in the abstract.

## 3. Novelty is judged against what is already known

For each contribution, write next to it the closest prior result and what is new relative to
it. Contributions that **confirm** a known effect in a new place (e.g. "ROC-AUC and AUC-PR can
rank classifiers differently", known since Davis & Goadrich 2006) do not count as novelty for
reviewers; they belong in the motivation or as a replication, not in the contribution list.

Do not undercut the paper. Sentences such as "we do not propose a new architecture" or "five of
the models are trivial by design" answer a question the reviewer had not asked and invite a
lower novelty score. State positively what kind of contribution it is (an evaluation-methodology
finding, a benchmark, a negative result with a mechanism) and cite papers of the same kind in
good venues to show the genre is valued.

## 4. Introduction: create a research space (Swales' CARS)

1. **Establish the territory** — why the topic matters, what is generally known (short).
2. **Establish the niche** — the gap: a counter-claim, a missing test, an open question.
   **Evidence for the gap is cited**, not asserted ("rarely tested because most studies have one
   region" needs a count or a review that shows it).
3. **Occupy the niche** — what this paper does, its main finding, and (optionally) the outline.

Mensh & Kording rule 6: paragraphs narrow from field gap to subfield gap to *this* gap; the last
paragraph states what fills it.

## 5. Context–Content–Conclusion at every scale

- **Paper:** Introduction = context, Results = content, Discussion = conclusion.
- **Paragraph:** first sentence gives context or the question; the body gives evidence; the last
  sentence gives the answer. A reader who reads only first and last sentences should follow the
  argument.
- **Abstract** (rule 5): context (broad → the gap) → what was done → key result(s) → what it
  means beyond this study. **One arc, not a list.** Three to four numbers at most; each number
  must serve the arc.
- **Results paragraphs** (rule 7): question → data and logic → declarative answer. Figure titles
  state conclusions; legends explain methods.
- **Discussion** (rule 8): how the gap was filled; limitations tied to literature; what changes
  for the field. **No new results in the Discussion** — move them to Results or the supplement.

Schimel's OCAR is the same idea as a story: Opening (context) → Challenge (the question) →
Action (methods and results) → Resolution (what the challenge's answer means).

## 6. Sentence level: reader expectations (Gopen & Swan 1990)

1. Keep the grammatical subject close to its verb.
2. Put the action in the verb, not in a noun ("we compared", not "a comparison was performed").
3. **Topic position** (sentence start): old information, linkage to the previous sentence.
4. **Stress position** (sentence end): the new, important information.
5. Old-to-new flow: each sentence's start picks up the previous sentence's end.
6. One unit, one function: a sentence, paragraph, or section makes one point.

## 7. Concision

Remove words that carry nothing ("it is important to note that", "in order to", "a total of");
prefer active voice where the actor matters; replace nominalisations with verbs; one idea per
sentence; cut repeated qualifiers. (See Hotaling 2020 for ten such rules with examples.)

## 8. Time allocation

Title, abstract, and figures are read by far more people than the rest; Methods least of all
(rule 9). Spend revision time in that order. Outline with one informal sentence per paragraph
before drafting; if the outline cannot be told to a colleague in a few minutes, the reader will
not follow the paper either (rule 10).

## Sources

- Mensh B, Kording K (2017) Ten simple rules for structuring papers. *PLOS Comput Biol*
  13(9): e1005619. https://doi.org/10.1371/journal.pcbi.1005619
- Gopen GD, Swan JA (1990) The science of scientific writing. *American Scientist* 78: 550–558.
- Swales JM (1990) *Genre Analysis: English in Academic and Research Settings*. Cambridge
  University Press — the CARS model.
- Schimel J (2012) *Writing Science: How to Write Papers That Get Cited and Proposals That Get
  Funded*. Oxford University Press — OCAR.
- Hotaling S (2020) Simple rules for concise scientific writing. *Limnology and Oceanography
  Letters* 5(6): 379–383. https://doi.org/10.1002/lol2.10165
- Whitesides GM (2004) Whitesides' group: writing a paper. *Advanced Materials* 16: 1375–1377.
- Rolnick D et al. (2024) Position: Application-driven innovation in machine learning. *ICML*,
  PMLR 235 — why application-driven ML work is undervalued by reviewers, and how to argue its
  contribution.
