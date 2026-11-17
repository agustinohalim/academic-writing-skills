"""Tests for thesis-writing scripts. Standard library only; pandoc is not needed.

    python -m unittest discover tests
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "plugins", "academic-writing", "skills", "thesis-writing")
SCRIPTS = os.path.join(SKILL, "scripts")
EKSPOR = os.path.join(SCRIPTS, "ekspor_naskah.py")
sys.path.insert(0, SCRIPTS)
import ekspor_naskah as ek  # noqa: E402

DOCUMENT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p><w:r><w:t>Isi</w:t></w:r></w:p>"
    '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
    '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" '
    'w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
)
STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:asciiTheme="minorHAnsi" w:hAnsiTheme="minorHAnsi"/><w:sz w:val="24"/>'
    "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>"
    '<w:spacing w:after="200"/></w:pPr></w:pPrDefault></w:docDefaults>'
    '<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/>'
    '<w:pPr><w:spacing w:before="180" w:after="180" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:rPr><w:sz w:val="20"/></w:rPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
    '<w:pPr><w:spacing w:before="480"/></w:pPr>'
    '<w:rPr><w:rFonts w:asciiTheme="majorHAnsi"/><w:b/><w:color w:val="4F81BD" '
    'w:themeColor="accent1"/><w:sz w:val="32"/></w:rPr></w:style>'
    "</w:styles>"
)


def docx_sintetis(document=DOCUMENT):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", STYLES)
    return buf.getvalue()


def bagian(data, nama):
    return zipfile.ZipFile(io.BytesIO(data)).read(nama).decode("utf-8")


class TestReferenceDocx(unittest.TestCase):
    def setUp(self):
        self.hasil = ek.ubah_reference_docx(docx_sintetis(), (4, 4, 3, 3), "Times New Roman", 12, 1.5)
        self.doc = bagian(self.hasil, "word/document.xml")
        self.gaya = bagian(self.hasil, "word/styles.xml")

    def test_a4_and_margins(self):
        self.assertIn('<w:pgSz w:w="11906" w:h="16838"/>', self.doc)
        self.assertEqual(self.doc.count("<w:pgSz"), 1)
        self.assertEqual(self.doc.count("<w:pgMar"), 1)
        m = re.search(r"<w:pgMar ([^>]*)/>", self.doc).group(1)
        self.assertIn('w:left="2268"', m)    # 4 cm
        self.assertIn('w:top="2268"', m)     # 4 cm
        self.assertIn('w:right="1701"', m)   # 3 cm
        self.assertIn('w:bottom="1701"', m)  # 3 cm

    def test_font_everywhere(self):
        fonts = re.findall(r"<w:rFonts\b[^>]*/>", self.gaya)
        self.assertTrue(fonts)
        for f in fonts:
            self.assertIn('w:ascii="Times New Roman"', f)
            self.assertNotIn("Theme", f)

    def test_size_and_spacing(self):
        self.assertIn('<w:sz w:val="24"/>', self.gaya)
        body = re.search(r'<w:style [^>]*w:styleId="BodyText".*?</w:style>', self.gaya, re.S).group(0)
        self.assertIn('<w:sz w:val="24"/>', body)
        self.assertIn('w:line="360"', body)  # 1.5 x 240
        self.assertNotIn('w:line="240"', body)
        default = re.search(r"<w:pPrDefault>.*?</w:pPrDefault>", self.gaya, re.S).group(0)
        self.assertIn('w:line="360"', default)
        self.assertEqual(self.gaya.count("<w:rPrDefault>"), 1)
        self.assertEqual(self.gaya.count("<w:pPrDefault>"), 1)

    def test_heading_black_and_keeps_size(self):
        self.assertNotIn("<w:color", self.gaya)
        heading = re.search(r'<w:style [^>]*w:styleId="Heading1".*?</w:style>', self.gaya, re.S).group(0)
        self.assertIn('<w:sz w:val="32"/>', heading)

    def test_other_parts_copied_and_valid_zip(self):
        z = zipfile.ZipFile(io.BytesIO(self.hasil))
        self.assertEqual(sorted(z.namelist()), ["[Content_Types].xml", "word/document.xml", "word/styles.xml"])

    def test_double_spacing_and_other_margins(self):
        hasil = ek.ubah_reference_docx(docx_sintetis(), (4, 3, 3, 3), "Arial", 11, 2)
        gaya = bagian(hasil, "word/styles.xml")
        doc = bagian(hasil, "word/document.xml")
        self.assertIn('w:line="480"', gaya)
        self.assertIn('w:ascii="Arial"', gaya)
        self.assertIn('<w:sz w:val="22"/>', gaya)
        self.assertIn('w:top="1701"', doc)

    def test_document_without_sectpr(self):
        doc = DOCUMENT.split("<w:sectPr>")[0] + "</w:body></w:document>"
        hasil = bagian(ek.ubah_reference_docx(docx_sintetis(doc)), "word/document.xml")
        self.assertIn("<w:sectPr><w:pgSz", hasil)


class TestChapters(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def tulis(self, nama, isi):
        jalur = os.path.join(self.tmp, nama)
        with open(jalur, "w", encoding="utf-8") as f:
            f.write(isi)
        return jalur

    def test_folder_order_natural_and_skips_private(self):
        for n in ("bab_10.md", "bab_2.md", "bab_1.md", "_catatan.md", "gambar.png"):
            self.tulis(n, "# x\n")
        nama = [os.path.basename(p) for p in ek.kumpulkan_bab([self.tmp])]
        self.assertEqual(nama, ["bab_1.md", "bab_2.md", "bab_10.md"])

    def test_explicit_order_kept(self):
        a, b = self.tulis("b.md", "B"), self.tulis("a.md", "A")
        self.assertEqual(ek.kumpulkan_bab([a, b]), [a, b])
        teks = ek.gabung_bab([a, b])
        self.assertLess(teks.index("B"), teks.index("A"))
        self.assertEqual(teks.count('w:type="page"'), 1)

    def test_placeholders_found(self):
        jalur = self.tulis("bab_4.md", "Responden [PERLU: jumlah dari data.xlsx].\nNilai ⬜.\nBersih.\nTODO cek\n")
        temuan = ek.cari_penanda([jalur])
        self.assertEqual([t[1] for t in temuan], [1, 2, 4])

    def test_latex_metadata(self):
        meta = ek.metadata_latex((4, 4, 3, 3), 12, 1.5, "report", "id")
        self.assertIn("documentclass: report", meta)
        self.assertIn('geometry: "left=4cm, top=4cm, right=3cm, bottom=3cm"', meta)
        self.assertIn("fontsize: 12pt", meta)
        self.assertIn("lang: id", meta)
        self.assertIn("labelformat=empty", meta)  # manual "Tabel 2.1" captions kept
        self.assertNotIn("labelformat", ek.metadata_latex((4, 4, 3, 3), 12, 1.5, "article", "en", True))
        self.assertNotIn("fontsize", ek.metadata_latex((4, 4, 3, 3), 13, 1.5, "report", "id"))

    def test_pdf_metadata_language_and_labels(self):
        meta = ek.metadata_pdf((4, 4, 3, 3), "Times New Roman", 12, 1.5, "id")
        self.assertIn("lang: id", meta)
        self.assertIn("#set figure(numbering: none)", meta)
        self.assertNotIn("numbering", ek.metadata_pdf((4, 4, 3, 3), "Arial", 11, 2, "en", True))

    def test_drop_notes_keeps_code_blocks(self):
        teks = "# Intro\n\n> Note: target journal X.\n> second line\n\nBody.\n\n```\n> not a note\n```\n"
        hasil = ek.buang_catatan(teks)
        self.assertNotIn("target journal", hasil)
        self.assertIn("Body.", hasil)
        self.assertIn("> not a note", hasil)
        jalur = self.tulis("m.md", teks)
        self.assertIn("target journal", ek.gabung_bab([jalur]))  # off by default (thesis quotations)
        self.assertNotIn("target journal", ek.gabung_bab([jalur], True))

    def test_latex_body_cleaned_for_journal_template(self):
        tex = ("\\begin{itemize}\n\\tightlist\n\\item a\n\\end{itemize}\n"
               "\\pandocbounded{\\includegraphics[keepaspectratio,alt={A {nested} alt}]{f.png}}\n"
               "\\includegraphics[width=0.8\\linewidth,alt={x}]{g.png}\n\\citep{k}\n")
        hasil, paket = ek.rapikan_isi_latex(tex)
        self.assertNotIn("\\tightlist", hasil)
        self.assertNotIn("pandocbounded", hasil)
        self.assertNotIn("alt=", hasil)
        self.assertIn("\\includegraphics[width=\\linewidth,keepaspectratio]{f.png}", hasil)
        self.assertIn("\\includegraphics[width=0.8\\linewidth]{g.png}", hasil)
        self.assertEqual(paket, ["graphicx", "natbib"])

    def test_latex_options_conflict(self):
        r = self.run_cli(self.tmp, "--out", os.path.join(self.tmp, "x"), "--latex", "--latex-body")
        self.assertEqual(r.returncode, 2)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
    def test_real_latex_export_keeps_cite_keys(self):
        self.tulis("bab_1.md", "# BAB I PENDAHULUAN\n\nTeks [@sutabri2012].\n")
        bib = os.path.join(self.tmp, "pustaka.bib")
        with open(bib, "w", encoding="utf-8") as f:
            f.write("@book{sutabri2012, author={Sutabri, Tata}, title={Analisis}, year={2012}}\n")
        keluar = os.path.join(self.tmp, "out", "Skripsi")
        r = self.run_cli(os.path.join(self.tmp, "bab_1.md"), "--out", keluar, "--latex", "--bib", bib)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(keluar + ".tex", encoding="utf-8") as f:
            tex = f.read()
        self.assertIn("\\chapter{BAB I PENDAHULUAN}", tex)
        self.assertIn("sutabri2012", tex)
        self.assertIn("left=4cm", tex)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "out", "pustaka.bib")))

    def test_english_need_placeholder_found(self):
        jalur = self.tulis("chapter_4.md", "Clean line.\nThe sample was [NEED: n from survey_clean.csv].\n")
        self.assertEqual([t[1] for t in ek.cari_penanda([jalur])], [2])

    def run_cli(self, *args):
        return subprocess.run([sys.executable, EKSPOR, *args], capture_output=True, text=True,
                              encoding="utf-8")

    def test_cli_refuses_placeholders_and_draft_passes_check(self):
        self.tulis("bab_1.md", "# BAB I\n\nData [PERLU: angka].\n")
        out = os.path.join(self.tmp, "keluar", "Skripsi")
        r = self.run_cli(self.tmp, "--out", out, "--docx")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Refused", r.stderr)
        self.assertIn("bab_1.md:3", r.stdout)
        r = self.run_cli(self.tmp, "--out", out, "--docx", "--draft")
        # with --draft the placeholder check passes; the run then needs pandoc
        self.assertNotIn("Refused", r.stderr)
        if shutil.which("pandoc") is None:
            self.assertEqual(r.returncode, 1)
            self.assertIn("pandoc not found", r.stderr)

    def test_cli_missing_input(self):
        r = self.run_cli(os.path.join(self.tmp, "tidak_ada.md"), "--out", "x")
        self.assertEqual(r.returncode, 2)


class TestSkillFile(unittest.TestCase):
    def test_frontmatter(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
            teks = f.read()
        m = re.match(r"---\n(.*?)\n---\n", teks, re.S)
        self.assertIsNotNone(m)
        meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
        self.assertEqual(meta.get("name"), "thesis-writing")
        self.assertGreater(len(meta.get("description", "")), 50)

    def test_referenced_files_exist(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
            teks = f.read()
        for rel in set(re.findall(r"`((?:references|scripts)/[\w\-./]+)`", teks)):
            self.assertTrue(os.path.exists(os.path.join(SKILL, rel)), rel)


if __name__ == "__main__":
    unittest.main()
