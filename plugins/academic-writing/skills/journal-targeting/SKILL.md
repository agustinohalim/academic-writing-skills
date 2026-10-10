---
name: journal-targeting
description: Choosing where to submit a journal article so it ends up published in an indexed journal (Scopus, Web of Science) — a target ladder of three or four journals chosen before writing, scope fit tested against recently published papers, index status verified on the official list on the day of submission (Scopus Sources, Discontinued Sources List), hijacked and predatory journals ruled out (Retraction Watch Hijacked Journal Checker, Think. Check. Submit.), metrics read correctly (CiteScore percentile vs SJR quartile vs Impact Factor), and the path after rejection (transfer offer, next rung, appeal). Use when the user asks which journal to target, whether a journal is indexed, Q1/Q2/Q3/Q4, "tembus Scopus", a call for papers or invitation email, a transfer offer, or where to send a rejected paper. Triggers in English and Indonesian — journal choice, target journal, Scopus indexed, quartile, CiteScore, SJR, predatory, hijacked, transfer offer, pilih jurnal, jurnal target, terindeks Scopus, kuartil, jurnal predator, jurnal bajakan, tawaran transfer, ditolak mau kirim ke mana.
---

# Journal Targeting

Respond in the user's language. This skill decides **where** a paper goes; how it is written is in
`scientific-article-writing`, and simultaneous or duplicate submission rules are in
`research-integrity`.

## Why this skill exists

"Getting into Scopus" fails in three ways, and only one of them is about the paper:

1. **Wrong fit.** Scope mismatch is the most common single reason for desk rejection
   (`scientific-article-writing/references/editor-and-reviewer-criteria.md`). A sound paper sent
   to a journal whose readers do not need it comes back in days.
2. **Wrong journal.** The journal was dropped from Scopus, is a hijacked clone of an indexed
   title, or never was indexed. The paper is published and counts for nothing — and it cannot be
   sent anywhere else.
3. **No plan after rejection.** Each rejection restarts the search, the reference style, and the
   formatting from zero, and months pass.

The ladder below addresses all three before the first submission.

## Derivation

```
one-sentence contribution + genre      (article plan, scientific-article-writing stage 1)
      ↓
long list (8–15)     where the closest prior work was published · publisher finders
      ↓
fit test             3 recent papers per journal · aims and scope · exclusion list
      ↓
verification         official index list · discontinued list · hijack check · Think.Check.Submit
      ↓
target ladder (3–4)  rung 1 → rung 2 → rung 3, each with format and reference style noted
      ↓
submit rung 1  →  decision  →  revise / transfer / next rung
```

The ladder is written **before** drafting, because the target journal fixes the reference
style, length, structure (e.g. highlights for Elsevier), and the readership the Introduction
speaks to.

## Step 1 — Long list

Start from evidence, not from rankings:

- **Where the closest prior work was published.** The 10–20 references the paper builds on most
  directly are the strongest signal of which journals' readers care. Count journals in the
  manuscript's own reference list.
- **Publisher finders**, which match an abstract against that publisher's own journals only:
  Elsevier JournalFinder, Springer Nature Journal Suggester, Wiley Journal Finder, IEEE
  Publication Recommender. Run more than one; each covers one publisher.
- **Scopus Sources** browsed by subject area, to see who else publishes the topic.
- **A different article type.** A dataset, software package, or method that the main paper
  uses can be its own short, citable article in a data, software, or methods journal (Elsevier
  calls these *research elements*). Such a paper is a separate contribution, not a slice of the
  main one: it must stand alone and the main paper cites it (salami rules in
  `research-integrity`).

A finder's suggestion is a candidate, never a decision: Elsevier states that each journal's
editors review independently and the finder guarantees nothing.

## Step 2 — Fit test

For each candidate, open the **three most recent research articles** on the same kind of
question and record, in one line each. A count makes "the journal publishes this" measurable:
for biomedical topics, query PubMed per journal (E-utilities `esearch`, `<topic terms> AND
<journal>[ta] AND 2023:2026[dp]`) and compare counts across candidates — a journal with zero
papers on the topic in four years is a scope risk whatever its aims say.

| Check | What to record |
|---|---|
| Aims and scope | The sentence that matches the paper — or "none" |
| Article type | Which types it takes (full article, letter or short communication, review, data, software, or method article) and whether it is invitation-only for that type |
| Recent papers | Do they share the genre (method, benchmark, dataset, critique)? Region-specific or general? |
| Exclusion list | Anything the guide for authors says it will not consider (e.g. minor model tweaks with small gains, unclear data splits) |
| Length and format | Word limit, structured abstract, highlights, graphical abstract, data statement |
| Reference style | Numbered or author–year |
| Cost and access | APC (open access) or subscription route with no fee; waiver eligibility |
| Speed | Time to first decision and acceptance-to-publication — Elsevier journal homepages show these under *Journal Insights* (speed, reach, impact) |
| AI policy | Where the AI statement goes (publisher default or stricter journal rule) |

If no sentence of the aims and scope fits and none of the recent papers resembles the
manuscript, drop the journal however high its metrics. Read the guide for authors in full, not
only the aims: exclusions often sit in the scope text (e.g. "studies focusing solely on AI will
only be considered when integrated into clinical systems"), and word limits differ by a factor of
two between otherwise similar journals. Publisher guide pages (ScienceDirect among them) refuse
automated fetches; open them in a browser.

Searching the recent literature of each candidate also turns up **close prior work the manuscript
does not cite yet**. Read it before submitting; citing the target journal's own recent papers on
the topic is part of showing fit.

## Step 3 — Verification (on the day of submission, not from memory)

Indexing status changes monthly. Never state that a journal "is Scopus-indexed" from training
data, a blog, or the journal's own website. Details and red flags:
`references/verification.md`.

1. **Scopus Sources** (`scopus.com/sources`, free, by title or ISSN): listed, coverage ongoing,
   recent years present.
2. **Discontinued Sources List** (Excel, updated monthly, linked from Elsevier's *Content policy
   and selection* page): the title is **not** on it.
3. **Web of Science status** (Master Journal List, `mjl.clarivate.com`): listed and **not on hold**,
   and no notice of an index investigation in the guide for authors. A journal dropped from one
   index is a warning for the other.
4. **Hijack check**: the URL you will submit through is the one Scopus links to (or the
   publisher's own platform), and the title is not on the Retraction Watch Hijacked Journal
   Checker.
5. **Think. Check. Submit.** checklist: submit only if most answers are yes.
5. If an institution or regulation requires a **specific metric** (e.g. a SJR quartile, a
   CiteScore percentile, a national index), check that exact metric at its source and note the
   year of the value.

Record the date, the source, and the result for each rung in the ladder file.

## Step 4 — The ladder

Three or four rungs, written into the article plan (or a `Target_Journals.md` beside the
manuscript):

| Rung | Journal | Why it fits (aims sentence + similar paper) | Index check (date, source) | Metric (which, year) | APC | Format notes |
|---|---|---|---|---|---|---|
| 1 | Ambitious but in scope | | | | | |
| 2 | Solid fit, broader acceptance | | | | | |
| 3 | Safe fit, still indexed | | | | | |

Rules for building it:

- **Every rung must pass Steps 2 and 3.** A "safe" rung that is not genuinely indexed is not safe.
- **Prefer rungs from the same publisher** where possible: a rejection can then come with a
  transfer offer, and the reference style and portal stay the same.
- **Aim high, but aim realistic.** A high Impact Factor often means a high rejection rate;
  choose rung 1 by fit first and prestige second. Scorecard section A
  (`scientific-article-writing/references/pre-submission-scorecard.md`) says how high: A below
  11 of 16 means the paper is not yet ready for an ambitious rung.
- **Deadlines.** If the paper must be *published* by a date (a promotion file, a grant report, a
  doctoral application), estimate each rung's submission-to-publication time and drop rungs that
  cannot make it. Credit rules often count the date of publication, not submission.

## Step 5 — After a decision

Details: `references/rejection-and-transfer.md`.

- **Desk rejection.** Read the reasons; map them to the scorecard. Scope → next rung as is.
  Contribution or framing → fix title, abstract, Introduction, and contribution list first.
  Never resend unchanged to a journal whose editor named a problem the next editor will also see.
- **Transfer offer** (Elsevier Article Transfer Service and similar). Nothing moves unless the
  author accepts. Check the proposed journal through Steps 2–3 exactly like a ladder rung; accept
  only if it would have qualified. Revising on the reviews before transferring is allowed and
  usually worth doing.
- **Rejection after review.** Address every reviewer comment before the next rung, even though
  the next journal will not see them: the same reviewers may be invited again.
- **Appeal** only for a demonstrable factual error in the evaluation, not disagreement.

## Hard rules

- **One journal at a time.** The manuscript goes nowhere else until a decision or a formal
  withdrawal (`research-integrity`).
- **Unsolicited invitations are not a route in.** An email inviting a submission, promising fast
  review and indexing, is a red flag until the journal passes Step 3 through the official list.
- **Index status is verified, never recalled.** State it with the date and source checked.
- **The author decides the target and presses submit.** The assistant prepares the ladder and
  the evidence.

## When to stop and ask

A candidate's index status is unclear or conflicting between sources; a rung requires an APC
the author has not approved; a deadline makes every rung infeasible; a transfer or special-issue
offer arrives; the institution's required metric differs from what the journal advertises.

## References

- `references/verification.md` — official lists, discontinued vs "no recent content", hijacked
  clones, predatory red flags, fake acceptance letters
- `references/metrics.md` — CiteScore, SJR, SNIP, Impact Factor: what each measures, quartile
  traps, which one an institution actually counts
- `references/rejection-and-transfer.md` — reading a rejection, transfer offers, moving down the
  ladder, appeals
- `references/sources.md` — official sources and Elsevier Researcher Academy modules, with the
  date checked
