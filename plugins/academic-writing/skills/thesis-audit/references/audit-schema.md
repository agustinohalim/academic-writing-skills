# audit.json

Written into the workspace after reading `manuscript_numbered.md`, `chain.json`, and
`machine.json`. `report_audit.py` checks it and refuses inconsistencies.

```json
{
  "level": "skripsi",
  "research_type": "system-development",
  "summary": "Three or four sentences: what the thesis does, whether its chain holds, the one thing that most needs fixing.",
  "modules": {
    "M01": {"status": "not_found", "coverage": "full", "basis": "All parts present; test scenarios in Lampiran B."},
    "M02": {"status": "found", "coverage": "full", "basis": "Two questions, one objective, two conclusions compared."},
    "M06": {"status": "not_assessable", "coverage": "limited", "basis": "Questionnaire items not included.",
            "missing": "the questionnaire (Lampiran) — needed to judge whether indicators measure the constructs"},
    "M12": {"status": "not_assessable", "coverage": "limited", "basis": "No source texts or similarity report supplied.",
            "missing": "Turnitin report or the source texts to compare against"}
  },
  "findings": [
    {
      "id": "F1",
      "module": "M02",
      "related": ["M09"],
      "title": "Question 2 (user acceptance) has no objective and no method",
      "severity": "major",
      "status": "confirmed",
      "confidence": "high",
      "line": 16,
      "quote": "Bagaimana tingkat penerimaan pengguna terhadap sistem?",
      "problem": "No objective, instrument, or analysis addresses acceptance, yet conclusion 2 answers it.",
      "fix": "Either drop the question and conclusion 2, or add an acceptance measure (e.g. UAT with a stated criterion) to chapter III and report it in chapter IV."
    }
  ],
  "defence_questions": [
    {
      "question": "Bagaimana Anda mengukur bahwa pengguna menerima sistem?",
      "why": "Conclusion 2 claims acceptance; no instrument is described.",
      "strong_answer": "Names the instrument, respondents, score and criterion — or concedes the claim and narrows it.",
      "findings": ["F1"]
    }
  ]
}
```

| Field | Rule |
|---|---|
| `modules` | Every module listed in `AUDIT.md`, once. `basis` always: what was checked, or why it does not apply |
| `coverage` | `full` / `partial` / `limited`; required for `found` and `not_found` |
| `missing` | Required for `not_assessable`: the input that would make the question answerable |
| `id` | Unique. Keep IDs stable between rounds (F1 stays F1 for the same problem) so progress can be tracked |
| `module` | The **one** module that owns the root cause. Other modules that see the same problem go in `related`; they do not get their own finding |
| `quote` | Exact text from one paragraph, 8–300 characters, no `L0000|` prefix. Missing-content findings quote where it should be, or the claim it undermines |
| `severity` / `status` / `confidence` | See `modules.md`. `critical` needs `confirmed` + `high`; `potential` can only be `minor` |
| `fix` | An action the author can take. "Perbaiki" or "clarify" alone is not a fix |
| `defence_questions` | Built only from findings (list their IDs). 5–10 for a skripsi; more for a disertasi |

Ownership rule of thumb: put the finding where fixing it starts. A conclusion that overclaims
because the method cannot support it belongs to M05, not M09; a number that differs between
chapters is M07 if the data is wrong, M10 if only the text is.
