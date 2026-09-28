"""Tests for manuscript-review scripts and the manuscript checker. Standard library only.

    python -m unittest discover tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "plugins", "academic-writing", "skills")
REVIEW = os.path.join(SKILLS, "manuscript-review", "scripts")
CHECK = os.path.join(SKILLS, "manuscript-proofreading", "scripts", "check_manuscript_en.py")

MANUSCRIPT = """# Label definitions decide whether evaluation conclusions transfer

## Abstract

We test whether model rankings transfer between regions. Rankings agree in 81% of resamples
under a per-unit target and disagree under a pooled target.

## 1. Introduction

Models are usually evaluated in one region (Smith et al. 2020). Whether rankings transfer is
rarely tested.

## 2. Results

Rankings agree in 81% of resamples under a per-unit target (Table 1).

**Table 1.** Agreement by target.

## 3. Discussion

A pooled target builds regional base rates into the label.

## References

Smith J, Doe A (2020) A study of evaluation. J Test 1:1-2
"""


def run(script, *args):
    return subprocess.run([sys.executable, script, *args], capture_output=True, text=True,
                          encoding="utf-8")


def finding(title, quote, severity="major", dimension="argument", line=1):
    return {"title": title, "severity": severity, "dimension": dimension, "line": line,
            "quote": quote, "problem": title + " matters.", "fix": "Do something specific."}


def role_file(ws, role, findings, score=3):
    data = {"role": role, "scores": {d: score for d in (
        "originality", "rigour", "evidence", "argument", "presentation", "literature", "significance")},
        "findings": findings}
    with open(os.path.join(ws, "findings", role + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f)


class ReviewFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ms = os.path.join(self.tmp, "paper.md")
        with open(self.ms, "w", encoding="utf-8") as f:
            f.write(MANUSCRIPT)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def prepare(self, name, src=None):
        ws = os.path.join(self.tmp, name)
        r = run(os.path.join(REVIEW, "prepare_review.py"), src or self.ms, "--out", ws)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return ws

    def consolidate(self, ws):
        r = run(os.path.join(REVIEW, "consolidate_review.py"), ws)
        with open(os.path.join(ws, "findings_final.json"), encoding="utf-8") as f:
            return r, json.load(f)

    def test_prepare_creates_workspace(self):
        ws = self.prepare("r1")
        for name in ("manuscript.md", "manuscript_numbered.md", "sections.json", "machine.json",
                     "meta.json", "PANEL.md"):
            self.assertTrue(os.path.exists(os.path.join(ws, name)), name)
        with open(os.path.join(ws, "manuscript_numbered.md"), encoding="utf-8") as f:
            self.assertTrue(f.readline().startswith("L0001| # Label"))
        self.assertEqual(run(os.path.join(REVIEW, "prepare_review.py"), self.ms, "--out", ws).returncode, 2)

    def test_quote_verification_and_line_correction(self):
        ws = self.prepare("r1")
        role_file(ws, "methods", [
            finding("Gap asserted", "Whether rankings transfer is\nrarely tested.", line=40),
            finding("Invented", "this sentence is not in the manuscript anywhere"),
        ])
        r, out = self.consolidate(ws)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(len(out["clusters"]), 1)
        self.assertEqual(out["clusters"][0]["line"], 10)  # wrapped quote found where it starts
        self.assertEqual(len(out["set_aside"]), 1)

    def test_consensus_and_decision(self):
        ws = self.prepare("r1")
        q = "Rankings agree in 81% of resamples under a per-unit target"
        role_file(ws, "editor", [finding("Scope overstated", q, severity="critical", line=16)])
        role_file(ws, "devils-advocate", [finding("Overgeneralised scope", q, severity="major", line=16)])
        _, out = self.consolidate(ws)
        top = out["clusters"][0]
        self.assertEqual(top["consensus"], 2)
        self.assertEqual(top["severity"], "critical")
        self.assertEqual(out["decision"], "Reject in current form")

    def test_schema_errors_reported(self):
        ws = self.prepare("r1")
        with open(os.path.join(ws, "findings", "domain.json"), "w", encoding="utf-8") as f:
            json.dump({"role": "domain", "scores": {"rigour": 9}, "findings": [{"title": "x"}]}, f)
        r, _ = self.consolidate(ws)
        self.assertEqual(r.returncode, 1)
        with open(os.path.join(ws, "report.md"), encoding="utf-8") as f:
            self.assertIn("Schema errors", f.read())

    def test_diff_resolved_open_and_not_rechecked(self):
        ws1 = self.prepare("r1")
        role_file(ws1, "editor", [finding("Title too narrow", "Label definitions decide whether evaluation", line=1)])
        role_file(ws1, "methods", [finding("Gap asserted", "Whether rankings transfer is", severity="minor", line=11)])
        role_file(ws1, "domain", [finding("Pooled target claim unsupported",
                                          "A pooled target builds regional base rates into the label.", line=22)])
        self.consolidate(ws1)
        ws2 = self.prepare("r2")
        role_file(ws2, "editor", [])  # editor ran again and no longer raises the title
        role_file(ws2, "domain", [finding("Pooled target claim still unsupported",
                                          "A pooled target builds regional base rates into the label.", line=22)])
        self.consolidate(ws2)
        r = run(os.path.join(REVIEW, "diff_review.py"), ws1, ws2)
        self.assertEqual(r.returncode, 1)  # a major issue is still open
        with open(os.path.join(ws2, "diff.md"), encoding="utf-8") as f:
            diff = f.read()
        self.assertIn("## Resolved (1)", diff)
        self.assertIn("## Still open (1)", diff)
        self.assertIn("## Not re-checked (1)", diff)  # methods did not run again


class Checker(unittest.TestCase):
    def test_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "paper.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(MANUSCRIPT.replace("agree in 81% of resamples\nunder", "agree in 82% of resamples\nunder"))
            r = run(CHECK, "--json", "--heavy", p)
            data = json.loads(r.stdout)
            self.assertTrue(any("82%" in x["message"] for x in data))
            self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
