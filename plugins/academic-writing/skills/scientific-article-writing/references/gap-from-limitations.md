# Finding the gap in the closest papers' own limitations

A gap stated as a general lesson ("simple baselines often match deep models", "case–control timing
biases AI studies") is already in the literature, so reviewers score originality low however good
the analysis is. A gap taken from the **closest papers' own limitations and untested claims** is
specific, verifiable, and hard to dismiss: the authors themselves said it was open. This file is the
procedure for finding one and for proving it is still open. Run it at stage 1, before the plan's
section A (question and answer) is approved, and again after any desk rejection for originality or
significance.

## 1. Read the closest papers in full

The closest papers are the ones whose claim, data, or design yours builds on or challenges — usually
two to five. Read the full text, not the abstract: Limitations, Discussion, Future work, and Methods.
Some papers (Nature-style) have no Limitations section; their caveats are spread over Results and
Methods, so read those too.

Copy every relevant sentence **verbatim**, with section name, source URL or PMCID, and the date read,
into the project's reference notes. Mark what was not read (supplement, peer-review file). Never
reconstruct a limitation from memory or from a summary.

## 2. List three kinds of candidate problem

| Kind | What it looks like | Example wording to look for |
|---|---|---|
| Stated limitation | the authors name it | "This study was limited…", "precise times … are not known", "a few hundred cases may not be enough" |
| Untested claim | asserted in Discussion without an analysis behind it | "it is reasonable to expect", "likely captured", "may", "whereas DL can…" |
| Unstated problem | a design feature the paper never mentions | software version, calendar years, date shifting, how controls were sampled |

Only the first kind may be written as "the authors acknowledge". The second is written as "the
authors suggest … without testing it". The third is your finding and is written as such; never
attribute it to them.

## 3. Can your data answer it?

For each candidate, write one line: answered by which analysis, with which number from the results
file — or "cannot be answered with these data". A limitation you share (same small dataset, same
single centre) is not a gap you fill; put it in your own Limitations.

## 4. Prove it is not solved yet

Search before claiming, and record the search (date, database, query, number of hits, what was
found) next to the verbatim quotes:

1. **Forward citations** of each closest paper — OpenAlex `filter=cites:<work id>`, Europe PMC
   citations, Google Scholar "cited by". Open each citing work's title/abstract; reviews and
   unrelated uses are listed, not ignored.
2. **Other users of the same data** — DataCite events on the dataset DOI, the data platform's
   publication list, full-text search for the dataset name.
3. **The general question** — PubMed/Scopus/web search for the problem stated without the dataset
   (e.g. "deep learning ECG versus standard ECG measurements"). This is the step that is most often
   skipped and the one that decides how far the claim may reach.

Then separate two levels:

- **Specific gap** (this claim, this dataset, this design) — open if no citing work or data user
  tested it.
- **General question** — if it is already answered elsewhere, do not claim it. Cite those studies,
  state the condition under which your result differs (data size, design, population), and present
  your result as complementary, not as a contradiction.

A web or OpenAlex search is not a systematic review; say so in the notes, and do not write "no
study has…" unless the search supports it. Prefer "we found no study that…, searching X and Y on
<date>".

## 5. Say what is new

An open gap is necessary, not sufficient. Running existing models on another dataset, or under a
stricter protocol, can fill a gap and still give the reader nothing to use. Before section A goes to
the author, complete this sentence in the gap record:

> After this paper, readers can <do or know X>, which <closest paper> could not give them.

X must be one of these:

| New | Test |
|---|---|
| Finding | an effect or mechanism not reported before, not a confirmation of a known one |
| Method or protocol | works on the data and beats the cheapest competitor |
| Resource | a dataset, benchmark, or tool others can use and could not build easily |
| Decision | a concrete choice in practice that changes because of the result |

An evaluation counts only when it produces one of these: the procedure that fixes the flaw, for
example, rather than the demonstration that the flaw exists. Score questions A2 and A8 of
`pre-submission-scorecard.md` now, against this sentence, instead of waiting for stage 6. A score of
0 on either triggers the stop rule below.

## 6. Write the gap

Introduction, last paragraph of the niche: "<Authors> state that <limitation, quoted or closely
paraphrased> and suggest that <untested claim>. Neither has been tested since (<search>). We test
both on the same data." Each contribution then answers one named limitation or claim, and the
Discussion returns to them in the same order.

## Stop rule

If every candidate is already solved, not answerable with your data, only a general lesson, or
adds nothing new under step 5, the paper has no usable gap: change the question, the data, or the genre (a short comment or
replication may still be possible) before writing more. Five rounds of revision cannot raise
originality that the question does not have.

## Why this exists

In October 2026 a re-analysis of a public ECG dataset went through five simulated review panels and
three editorial rejections. Each round fixed the previous critical issue and the panel found a new
one; originality stayed at 2–3 because the paper claimed a general lesson ("simple baselines beat
waveform models") that larger studies had already answered the other way. Reading the original
paper's Limitations afterwards showed that its authors had conceded the exact weakness the
re-analysis measured (control recording times not known) and had asserted, untested, that the
network captured the information in standard ECG measurements — a specific, open gap that had been
available from the start.
