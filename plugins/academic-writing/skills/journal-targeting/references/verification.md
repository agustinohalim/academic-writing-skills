# Verifying a Journal

Do this for every rung of the ladder, on the day of submission, and record date and source.

## 1. Is it in Scopus now?

Scopus publishes its title lists openly; no subscription is needed.

| Source | What it answers |
|---|---|
| Scopus Sources — `https://www.scopus.com/sources.uri` | Search by title, publisher, or ISSN. Shows coverage years, CiteScore, and whether coverage is ongoing |
| Discontinued Sources List — Excel linked from Elsevier's *Content policy and selection* page, updated monthly | Titles whose forward coverage Scopus stopped, with the volume/issue where indexing ended |
| Source title list (Excel), same page | The full list of indexed titles |

**One download covers the whole ladder.** The monthly Excel file is not only the discontinued
list: its first sheet is the full source list with, per title, *Active or Inactive*, coverage years,
*Open Access Status*, publisher, and subject codes; further sheets list discontinued titles (with
the last covered issue) and titles accepted but not yet added. Download it once and look up every
candidate by exact title or ISSN with a short script, instead of searching the web per journal.
A coverage range that stops before the current year (e.g. `2020-2024`) is a reason to drop the
title even if it says *Active*.

**Two kinds of "discontinued".** A title can show "discontinued" on Scopus Sources without being
on the Discontinued Sources List: Scopus marks a title that way when it has received no new
content from the publisher for about three years, or when the publisher stopped publishing.
The first is reversible once content arrives. Only the Discontinued Sources List records a
decision by the Content Selection and Advisory Board (CSAB) to stop coverage.

**How a journal gets dropped.** Elsevier flags titles for re-evaluation in two ways: concerns
raised about publication standards (ethics, integrity), and an outlier model that looks for
unexpected patterns in output volume, citation graphs, author collaborations, or content.
During re-evaluation the content flow is suspended. The CSAB then continues or discontinues
coverage. Content already indexed usually stays, but **papers published after the cut-off are
not indexed** — this is what makes a recently flagged journal dangerous.

Warning signs that a title may be under re-evaluation or heading for it: a sudden jump in the
number of papers per issue, many special issues outside the journal's field, very short review
times, a large share of papers from a few countries or institutions, or a gap in Scopus
coverage for the latest issues.

**Lists from third parties** (university announcements, blogs, Scimago pages) are leads only.
Scimago (SJR) is a different database built on Scopus data and can lag behind Scopus decisions.
Confirm on the Scopus list itself.

**Open-access status lags too.** A journal that flipped to full open access can still be marked
non-OA in Scimago's export (seen in October 2026 for *EP Europace*, fully OA since its 2023
volume). When the ladder excludes APC journals, confirm the model on the publisher's or society's
own page, not on an aggregator.

## 2. Is it the real journal? (hijacked clones)

A hijacked journal copies the title, ISSN, and metadata of a legitimate indexed journal and
runs a fake website that takes submissions and fees. Clones have repeatedly managed to get
content into Scopus under the legitimate title.

- Check the **Retraction Watch Hijacked Journal Checker** (a public spreadsheet maintained with
  Anna Abalkina; several hundred entries, growing by dozens each year).
- Reach the journal's website **from the Scopus Sources entry** or the publisher's own platform,
  never from an email or a search result. Compare the domain.
- Red flags: a domain unlike the publisher's, a submission address on a free email service,
  payment requested before review, "guaranteed Scopus indexing", acceptance in days.

## 3. Is it trustworthy? (predatory journals)

Use the **Think. Check. Submit.** checklist (`thinkchecksubmit.org`), supported by publishers and
organisations including DOAJ and OASPA. Submit only if you can answer yes to most items. Sample
items: do you or your colleagues know the journal; is the peer-review type stated; can the
publisher be identified and contacted; is the publisher a member of a recognised industry
initiative (COPE, OASPA, DOAJ for open access).

Caveats: the checklist assumes a track record, so new journals are hard to judge; COPE advises
that lists of predatory journals be scrutinised as closely as the journals themselves, and that
lists without transparent criteria should not be relied on.

## 4. Fake acceptance letters

Elsevier Researcher Academy has a module on identifying fake acceptance letters. Practical
checks: the decision appears in the journal's own submission system (Editorial Manager, Snapshot,
ScholarOne), not only in an email; the sender domain belongs to the publisher; no payment link
to a personal or unrelated account.

## Recording the check

In the ladder table, per rung: `Scopus Sources: ongoing, 2026 issues present (checked
2026-10-09); not on Discontinued List Aug 2026; not on RW Hijacked Checker; TCS 9/10 yes`.
