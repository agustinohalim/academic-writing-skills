"""Tests for thesis-audit scripts. Standard library only.

    python -m unittest discover tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "plugins", "academic-writing", "skills", "thesis-audit", "scripts")
PREPARE = os.path.join(AUDIT, "prepare_audit.py")
REPORT = os.path.join(AUDIT, "report_audit.py")
sys.path.insert(0, AUDIT)
from modul import modul_untuk  # noqa: E402

SKRIPSI = """# ABSTRAK

Penelitian ini membangun sistem informasi inventaris. Pengujian black-box menunjukkan 95% fungsi
berjalan dan kepuasan pengguna 4,2 dari 5.

# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Pencatatan inventaris di Toko Maju masih manual (Sutabri, 2012). Menurut Pressman dkk. (2019),
perangkat lunak yang baik perlu diuji sebelum dipakai.

## 1.2 Rumusan Masalah

1. Bagaimana merancang sistem informasi inventaris untuk Toko Maju?
2. Bagaimana tingkat penerimaan pengguna terhadap sistem?

## 1.3 Tujuan Penelitian

1. Merancang sistem informasi inventaris untuk Toko Maju.

# BAB II TINJAUAN PUSTAKA

Sistem informasi adalah kumpulan komponen yang saling terkait (Sutabri, 2012). Pengujian
black-box dijelaskan oleh Myers (2011).

# BAB III METODOLOGI PENELITIAN

Metode pengembangan memakai waterfall. Kebutuhan dikumpulkan lewat wawancara.
Tabel 3.1 memuat kebutuhan fungsional.

**Tabel 3.1** Kebutuhan fungsional

| No | Kebutuhan |
|---|---|
| 1 | Mencatat barang |

**Gambar 3.1** Diagram use case

![Gambar 3.2 Diagram aktivitas](gambar/aktivitas.png)

Alur pencatatan ditunjukkan pada Gambar 3.2.

# BAB IV HASIL DAN PEMBAHASAN

Pengujian black-box menunjukkan 95% fungsi berjalan (Tabel 4.1). Pengguna menyatakan puas.

# BAB V PENUTUP

## 5.1 Kesimpulan

1. Sistem informasi inventaris berhasil dirancang.
2. Pengguna menerima sistem dengan baik.

# DAFTAR PUSTAKA

Pressman, R.S., 2019. Software Engineering. McGraw-Hill.
Sutabri, T., 2012. Analisis Sistem Informasi. Andi.
Kotler, P., 2016. Marketing Management. Pearson.
"""


def run(script, *args):
    return subprocess.run([sys.executable, script, *args], capture_output=True, text=True, encoding="utf-8")


def docx(path, paragraphs):
    """Minimal .docx: (style, text) pairs."""
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    body = ""
    for style, text in paragraphs:
        ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
        body += f"<w:p>{ppr}<w:r><w:t>{text}</w:t></w:r></w:p>"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<?xml version="1.0"?><w:document {w}><w:body>{body}</w:body></w:document>')


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "skripsi.md")
        with open(self.src, "w", encoding="utf-8") as f:
            f.write(SKRIPSI)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def prepare(self, src=None, level="skripsi"):
        ws = os.path.join(self.tmp, "ws")
        r = run(PREPARE, src or self.src, "--level", level, "--out", ws, "--force")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return ws

    def load(self, ws, name):
        with open(os.path.join(ws, name), encoding="utf-8") as f:
            return json.load(f) if name.endswith(".json") else f.read()


class Prepare(Base):
    def test_machine_checks(self):
        ws = self.prepare()
        msgs = [m["message"] for m in self.load(ws, "machine.json") if m["weight"] == "heavy"]
        joined = "\n".join(msgs)
        self.assertIn("rumusan 2, tujuan 1, kesimpulan 2", joined)
        self.assertIn("sitasi 'Myers 2011'", joined)
        self.assertIn("Kotler", joined)
        self.assertNotIn("Pressman", joined)  # "Pressman dkk. (2019)" matched its entry
        self.assertIn("Tabel 4.1 dirujuk", joined)
        self.assertIn("Gambar 3.1 tidak pernah dirujuk", joined)
        self.assertNotIn("Tabel 3.1", joined)  # "Tabel 3.1 memuat ..." is a reference, not a caption
        self.assertNotIn("Gambar 3.2", joined)  # caption given as image alt text
        self.assertIn("'4,2'", joined)
        self.assertNotIn("'95%'", joined)
        meta = self.load(ws, "meta.json")
        self.assertEqual(meta["lang"], "id")
        self.assertNotIn("M14", meta["modules"])

    def test_chain_items(self):
        ch = self.load(self.prepare(), "chain.json")
        self.assertEqual(len(ch["rumusan"]["items"]), 2)
        self.assertEqual(ch["kesimpulan"]["section"], "5.1 Kesimpulan")
        self.assertEqual(ch["tujuan"]["items"][0]["line"], 20)

    def test_docx_conversion(self):
        p = os.path.join(self.tmp, "s.docx")
        docx(p, [("", "BAB I"), ("", "PENDAHULUAN"), ("", "1.2 Rumusan Masalah"),
                 ("ListParagraph", "Bagaimana merancang sistem?"), ("Heading2", "Tujuan Penelitian"),
                 ("", "Penelitian ini bertujuan merancang sistem.")])
        ws = self.prepare(p)
        md = self.load(ws, "manuscript.md")
        self.assertIn("# BAB I", md)
        self.assertIn("## 1.2 Rumusan Masalah", md)
        self.assertIn("## Tujuan Penelitian", md)
        self.assertEqual(self.load(ws, "chain.json")["tujuan"]["form"], "paragraph")

    def test_dissertation_has_thread_module(self):
        self.assertIn("M14", self.load(self.prepare(level="disertasi"), "meta.json")["modules"])


def audit(findings, status=None, questions=()):
    mods = {m: {"status": "not_found", "coverage": "full", "basis": "checked"} for m in modul_untuk("skripsi")}
    for mid, st in (status or {}).items():
        mods[mid] = {"status": st, "coverage": "partial", "basis": "checked",
                     **({"missing": "instrument not attached"} if st == "not_assessable" else {})}
    return {"level": "skripsi", "research_type": "system-development", "summary": "s",
            "modules": mods, "findings": findings, "defence_questions": list(questions)}


def f(id_, module, quote, severity="major", status="confirmed", confidence="high"):
    return {"id": id_, "module": module, "title": id_ + " title", "severity": severity, "status": status,
            "confidence": confidence, "line": 1, "quote": quote, "problem": "p", "fix": "do x"}


class Report(Base):
    def write(self, ws, data):
        with open(os.path.join(ws, "audit.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return run(REPORT, ws)

    def test_consistent_audit(self):
        ws = self.prepare()
        r = self.write(ws, audit(
            [f("F1", "M02", "Bagaimana tingkat penerimaan pengguna terhadap sistem?", "critical"),
             f("F2", "M09", "Pengguna menerima sistem dengan baik.", "minor", "potential", "medium")],
            {"M02": "found", "M09": "found", "M06": "not_assessable"},
            [{"question": "Bagaimana penerimaan diukur?", "why": "w", "strong_answer": "a", "findings": ["F1"]}]))
        self.assertEqual(r.returncode, 0, r.stdout)
        rep = self.load(ws, "report.md")
        self.assertIn("Belum layak diuji", rep)
        self.assertIn("instrument not attached", rep)
        out = self.load(ws, "audit_final.json")
        self.assertEqual(out["findings"][0]["line"], 16)  # corrected from the quote
        self.assertEqual(out["findings"][0]["chapter"], "BAB I PENDAHULUAN")
        fb = self.load(ws, "feedback.md")
        self.assertIn("## BAB I PENDAHULUAN", fb)
        self.assertNotIn("confidence", fb)
        self.assertIn("Bagaimana penerimaan diukur?", fb)

    def test_inconsistencies_rejected(self):
        ws = self.prepare()
        data = audit(
            [f("F1", "M02", "Bagaimana tingkat penerimaan pengguna terhadap sistem?", "critical", "likely"),
             f("F2", "M09", "Pengguna menerima sistem dengan baik.", "major", "potential"),
             f("F3", "M05", "this quote is not in the thesis at all")],
            {"M02": "found", "M05": "found"},
            [{"question": "q", "findings": ["F9"]}])
        del data["modules"]["M13"]
        r = self.write(ws, data)
        self.assertEqual(r.returncode, 1)
        errs = "\n".join(self.load(ws, "audit_final.json")["errors"])
        self.assertIn("F1: critical needs status 'confirmed'", errs)
        self.assertIn("F2: a potential issue can only be minor", errs)
        self.assertIn("M09: status 'not_found' but 1 verified finding", errs)
        self.assertIn("M05: status 'found' but no verified finding", errs)  # F3 set aside
        self.assertIn("M13: module missing", errs)
        self.assertIn("unknown finding 'F9'", errs)


if __name__ == "__main__":
    unittest.main()
