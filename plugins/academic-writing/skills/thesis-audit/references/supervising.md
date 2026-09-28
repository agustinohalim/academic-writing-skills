# Supervising with the audit

For the lecturer. The audit is a reading aid, not a verdict: you decide what goes to the student.

## Before the first round

- **Get the faculty template and the programme's skripsi guideline** (pedoman penulisan). Where
  they differ from `modules.md` — chapter names, required appendices, citation style — they win.
  Note the differences in the panel note you give the audit.
- **Agree the research type early.** Most rework in S1 comes from a chain that was never set:
  a system-development skripsi that sprouts a survey question in chapter I, or a survey that
  claims to "build" something. Fix `research_type` at proposal stage and audit against it.

## Each round

1. Prepare a new workspace per draft: `audit/<student>/<YYYY-MM-DD>`.
2. Run the audit, then `report_audit.py`. Read `report.md` yourself first.
3. **Edit before sending.** Remove findings you disagree with (re-run so the counts stay
   honest), soften or sharpen wording, add what the audit cannot know (what was agreed in the
   last meeting, the site's constraints).
4. Send `feedback.md`, or use it as the agenda for the meeting. It lists the top items per
   chapter, in plain actions, without internal statuses.
5. Next draft: prepare a new workspace, then compare the two drafts before auditing again:

   ```bash
   python "<manuscript-review>/scripts/impact_review.py" audit/budi/2026-10-01 audit/budi/2026-10-22
   ```

   It shows which chapters the student edited, and numbers or terms changed in one place but
   left in another — the most common result of a hurried revision.

Keep finding IDs stable between rounds when the same problem persists; the student can then see
which items are closed.

## Order of work matters

`feedback.md` puts upstream problems first on purpose. A student who fixes chapter IV tables
while the rumusan masalah is still changing will fix them twice. Chain (M02) and method (M05)
problems go first; citations and numbering last, unless they are all that is left.

**Limit each round.** Twelve items (the default `--top`) is already a lot for an S1 student.
The rest waits for the next round; the report keeps them.

## What not to do

- Do not rewrite the student's text for them, and do not send model-written paragraphs as
  "contoh". The skripsi is assessed as their work. Explain the problem and the action; they write.
- Do not tell a student their text is AI-written or plagiarised on the audit's word. Style is
  not evidence. If you suspect it, ask for drafts, data, and the Turnitin report, and follow the
  faculty's procedure.
- Do not audit on external services. A skripsi draft is unpublished student work: keep
  workspaces local, out of public repositories, and delete them when the student graduates if
  the faculty's retention rules say so.

## Before the defence (sidang)

Run a final audit on the version submitted for examination. `defence_questions` in the report
are what examiners are likely to ask, each tied to a weakness in the text. Give the student the
questions (they are in `feedback.md`), not the model answers: preparing the answer is the
exercise.
