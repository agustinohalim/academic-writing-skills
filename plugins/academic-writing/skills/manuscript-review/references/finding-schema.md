# Finding Schema

Each role writes one file, `findings/<role>.json`, in the review workspace:

```json
{
  "role": "methods",
  "reviewer_profile": "Evaluates spatial and temporal validation in remote-sensing ML",
  "summary": "Two or three sentences: the role's overall judgement.",
  "scores": {
    "originality": 3, "rigour": 2, "evidence": 3, "argument": 3,
    "presentation": 4, "literature": 3, "significance": 3
  },
  "strongest_counterargument": "devils-advocate only: the best argument against the main claim",
  "findings": [
    {
      "id": "M1",
      "title": "Normalisation statistics computed before the train/test split",
      "severity": "critical",
      "dimension": "rigour",
      "line": 214,
      "quote": "All features were standardised using the mean and standard deviation of the full dataset.",
      "problem": "What is wrong and why it matters for the claim.",
      "fix": "What the author should do, concretely.",
      "confidence": "high"
    }
  ]
}
```

| Field | Rule |
|---|---|
| `scores` | All seven dimensions, integers 1–5. 3 = typical for a solid submission to the target journal |
| `severity` | `critical` (a main claim may be wrong or unsupported) · `major` (a reviewer will certainly require it) · `minor` (improves the paper) |
| `dimension` | One of `originality`, `rigour`, `evidence`, `argument`, `presentation`, `literature`, `significance` |
| `line` | From `manuscript_numbered.md`; the script corrects it if the quote is found elsewhere |
| `quote` | **Exact** text copied from the manuscript, 8–300 characters, from a single paragraph. Markdown bold and backticks may be dropped. Findings whose quote is not found are set aside |
| `problem` | Why it matters, in terms of the paper's claims |
| `fix` | An action. "Clarify" alone is not a fix |
| `confidence` | `high` / `medium` / `low` — how sure the role is that this is a real problem |

Findings about something **absent** (a missing baseline, a missing limitation) quote the sentence
where it should appear or the claim it undermines.

## Not assessable

Optional top-level list, next to `findings`:

```json
"not_assessable": [
  {"question": "Is the test split by patient rather than by recording?",
   "missing": "the manuscript does not describe how records were assigned to splits"}
]
```

Use it when a question in the role's remit cannot be answered from the manuscript at all.
It is not a finding and does not affect the decision; the report lists it so that silence is not
read as a pass. If the absence itself is a defect a journal reviewer would raise, write a finding
instead (or as well). Each entry needs both `question` and `missing`.
