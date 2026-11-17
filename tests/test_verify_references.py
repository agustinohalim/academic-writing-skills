"""Tests for research-integrity/scripts/verify_references.py. Standard library only, no network:
fetch_json is replaced with canned Crossref and OpenAlex payloads.

    python -m unittest discover tests
"""

import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugins", "academic-writing", "skills", "research-integrity", "scripts")
sys.path.insert(0, SCRIPTS)
import verify_references as vr  # noqa: E402


def crossref_work(title, year, family, doi):
    return {"status": "ok", "message": {
        "title": [title], "issued": {"date-parts": [[year, 3, 1]]},
        "author": [{"family": family, "given": "A."}], "DOI": doi,
        "container-title": ["Journal of Tests"]}}


def openalex_work(title, year, name, doi):
    return {"display_name": title, "publication_year": year, "doi": f"https://doi.org/{doi}",
            "authorships": [{"author": {"display_name": name}}]}


class FakeNet:
    """Routes URLs to payloads by prefix; records every URL requested."""

    def __init__(self, routes):
        self.routes, self.urls = routes, []

    def __call__(self, url):
        self.urls.append(url)
        for prefix, payload in self.routes:
            if url.startswith(prefix):
                return payload
        return None


DOI_A = "10.1234/jt.2020.001"
TITLE_A = "Deep learning for crop yield prediction in smallholder farms"

MANUSCRIPT = f"""# Pendahuluan

Teks (Wibowo, 2020).

# Daftar Pustaka

Wibowo, A. (2020). {TITLE_A}. *Journal of Tests*, 12(3), 1–10. https://doi.org/{DOI_A}.

Sugiyono. (2019). *Metode penelitian kuantitatif, kualitatif, dan R&D*. Bandung: Alfabeta.

# Lampiran

Kuesioner (2021). Ini bukan entri pustaka yang harus diperiksa sama sekali.
"""


class Base(unittest.TestCase):
    def setUp(self):
        self._fetch = vr.fetch_json
        self._settings = dict(vr.SETTINGS)

    def tearDown(self):
        vr.fetch_json = self._fetch
        vr.SETTINGS.clear()
        vr.SETTINGS.update(self._settings)

    def net(self, routes):
        vr.fetch_json = FakeNet(routes)
        return vr.fetch_json

    def check(self, text):
        return vr.check_entry(vr.parse_entry(text), cache={})


class Parsing(Base):
    def test_indonesian_section_stops_at_appendix(self):
        lines = vr.find_section(MANUSCRIPT)
        entries = vr.split_entries(lines)
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0].startswith("Wibowo"))
        self.assertFalse(any("Kuesioner" in e for e in entries))

    def test_english_heading_and_last_section_wins(self):
        text = ("Contents\n\nReferences\n\n# Intro\n\nBody.\n\n## References\n\n"
                "Smith, J. (2021). A title long enough here. Journal, 1(1), 1-2.\n\n# Appendix A\n\nx")
        entries = vr.split_entries(vr.find_section(text))
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0].startswith("Smith"))

    def test_no_heading_returns_none(self):
        self.assertIsNone(vr.find_section("# Intro\n\nNo list here."))

    def test_one_entry_per_line_and_wrapped_lines(self):
        lines = [
            "Smith, J. (2020). First title of a paper. Journal A, 1(2), 3-4.",
            "Doe, A., & Roe, B. (2019). Second title that wraps",
            "  onto a second line. Journal B, 5, 6-7.",
            "[3] C. Lee, \"Third paper title here,\" IEEE Trans., vol. 2, 2018.",
        ]
        entries = vr.split_entries(lines)
        self.assertEqual(len(entries), 3)
        self.assertIn("onto a second line", entries[1])
        self.assertTrue(entries[2].startswith("C. Lee"))

    def test_doi_extraction(self):
        e = vr.parse_entry(f"Wibowo, A. (2020). Title here please. J, 1. https://doi.org/{DOI_A.upper()}.")
        self.assertEqual(e["doi"], DOI_A)
        e = vr.parse_entry("Lee, C. (2020). Title here please. Lancet. doi:10.1016/S0140-6736(20)30183-5)")
        self.assertEqual(e["doi"], "10.1016/s0140-6736(20)30183-5")
        e = vr.parse_entry("Lee, C. (2020). Title here please. Journal, 4(1).")
        self.assertIsNone(e["doi"])

    def test_fields(self):
        e = vr.parse_entry(f"Wibowo, A., & Sari, D. (2020). {TITLE_A}. Journal of Tests, 12(3), 1-10.")
        self.assertEqual((e["author"], e["year"], e["title"]), ("Wibowo", 2020, TITLE_A))
        e = vr.parse_entry('[1] J. Smith and A. Doe, "A quoted IEEE title," IEEE Access, vol. 8, 2020.')
        self.assertEqual((e["author"], e["title"]), ("Smith", "A quoted IEEE title"))

    def test_classification(self):
        self.assertEqual(vr.parse_entry("Sugiyono. (2019). Metode penelitian. Bandung: Alfabeta.")["type"], "book")
        self.assertEqual(vr.parse_entry("Budi, S. (2021). Sistem inventaris toko [Skripsi]. Universitas Maju.")["type"], "thesis")
        self.assertEqual(vr.parse_entry("Undang-Undang Nomor 12 Tahun 2012 tentang Pendidikan Tinggi.")["type"], "regulation")
        self.assertEqual(vr.parse_entry("Ani, R. (2022). Implementasi peraturan desa. Jurnal Hukum, 3(1), 1-9.")["type"], "article")

    def test_bibtex(self):
        bib = ("@article{w2020, author = {Wibowo, Adi and Sari, Dewi}, title = {" + TITLE_A + "},\n"
               "  journal = {Journal of Tests}, year = 2020, doi = {" + DOI_A + "}}\n"
               "@book{s2019, author = {Sugiyono}, title = {Metode Penelitian}, publisher = {Alfabeta}, year = {2019}}")
        entries = vr.parse_bib(bib)
        self.assertEqual(len(entries), 2)
        self.assertEqual((entries[0]["doi"], entries[0]["author"], entries[0]["year"]), (DOI_A, "Wibowo", 2020))
        self.assertEqual(entries[1]["type"], "book")

    def test_docx(self):
        w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        body = (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>DAFTAR PUSTAKA</w:t></w:r></w:p>'
                f'<w:p><w:r><w:t>Wibowo, A. (2020). {TITLE_A}. J, 1(1).</w:t></w:r></w:p>'
                f'<w:p><w:r><w:t>Sugiyono. (2019). Metode penelitian. Bandung: Alfabeta.</w:t></w:r></w:p>')
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.docx")
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("word/document.xml", f"<w:document {w}><w:body>{body}</w:body></w:document>")
            entries = vr.load_entries(p, whole=False)
        self.assertEqual(len(entries), 2)


class Checking(Base):
    def test_verified(self):
        self.net([(f"{vr.CROSSREF}/works/", crossref_work(TITLE_A, 2020, "Wibowo", DOI_A))])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests, 12(3). https://doi.org/{DOI_A}")
        self.assertEqual(r["status"], "verified", r["note"])

    def test_doi_mismatch(self):
        self.net([(f"{vr.CROSSREF}/works/", crossref_work("Ocean salinity trends in the North Atlantic", 2020, "Hansen", DOI_A))])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests. https://doi.org/{DOI_A}")
        self.assertEqual(r["status"], "doi_mismatch")

    def test_doi_not_found_in_either(self):
        net = self.net([])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests. https://doi.org/{DOI_A}")
        self.assertEqual(r["status"], "doi_not_found")
        self.assertTrue(any(u.startswith(vr.CROSSREF) for u in net.urls))
        self.assertTrue(any(u.startswith(f"{vr.OPENALEX}/works/doi:") for u in net.urls))

    def test_openalex_fallback_verifies(self):
        self.net([(f"{vr.OPENALEX}/works/doi:", openalex_work(TITLE_A, 2020, "Adi Wibowo", DOI_A))])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests. https://doi.org/{DOI_A}")
        self.assertEqual((r["status"], r["source"]), ("verified", "OpenAlex"))

    def test_partial_year_off_by_one(self):
        self.net([(f"{vr.CROSSREF}/works/", crossref_work(TITLE_A, 2021, "Wibowo", DOI_A))])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests. https://doi.org/{DOI_A}")
        self.assertEqual(r["status"], "partial")
        self.assertIn("year 2020 vs record 2021", r["note"])

    def test_found_without_doi_suggests_doi(self):
        search = {"message": {"items": [crossref_work(TITLE_A, 2020, "Wibowo", DOI_A)["message"]]}}
        net = self.net([(f"{vr.CROSSREF}/works?", search)])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests, 12(3), 1-10.")
        self.assertEqual(r["status"], "found")
        self.assertEqual(r["found_doi"], DOI_A)
        self.assertIn("verify, then add", r["note"])
        self.assertIn("query.bibliographic=", net.urls[0])
        self.assertIn("rows=2", net.urls[0])

    def test_tie_prefers_cited_article_number_over_notice(self):
        notice = crossref_work(TITLE_A, 2020, "Wibowo", "10.1234/jt.q902")["message"]
        notice["type"] = "correction"
        real = crossref_work(TITLE_A, 2020, "Wibowo", "10.1234/jt-2020-078378")["message"]
        self.net([(f"{vr.CROSSREF}/works?", {"message": {"items": [notice, real]}})])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests, 12, e078378.")
        self.assertEqual(r["found_doi"], "10.1234/jt-2020-078378")
        self.assertIn("10.1234/jt.q902", r["note"])

    def test_wrong_hit_not_accepted(self):
        search = {"message": {"items": [crossref_work("Ocean salinity trends", 2020, "Hansen", "10.9/x")["message"]]}}
        self.net([(f"{vr.CROSSREF}/works?", search), (f"{vr.OPENALEX}/works?", {"results": []})])
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. Journal of Tests, 12(3), 1-10.")
        self.assertEqual(r["status"], "not_found")

    def test_indonesian_not_found_gets_manual_pointers(self):
        self.net([(f"{vr.CROSSREF}/works?", {"message": {"items": []}}),
                  (f"{vr.OPENALEX}/works?", {"results": []})])
        r = self.check("Putri, D., dkk. (2021). Analisis kepuasan pengguna aplikasi desa. "
                       "Jurnal Sistem Informasi Nusantara, 4(2), 11-20.")
        self.assertEqual(r["status"], "not_found")
        self.assertIn(vr.GARUDA, r["manual"])
        self.assertIn(vr.SINTA, r["manual"])
        self.assertIn("Analisis kepuasan pengguna aplikasi desa", r["manual"])

    def test_book_not_checkable_online(self):
        net = self.net([])
        r = self.check("Sugiyono. (2019). Metode penelitian kuantitatif. Bandung: Alfabeta.")
        self.assertEqual(r["status"], "not_checkable_online")
        self.assertIn("catalogue", r["note"])
        self.assertEqual(net.urls, [])

    def test_network_error_is_not_heavy(self):
        def boom(url):
            raise vr.NetworkError("offline")
        vr.fetch_json = boom
        r = self.check(f"Wibowo, A. (2020). {TITLE_A}. J. https://doi.org/{DOI_A}")
        self.assertEqual(r["status"], "error")


class Privacy(Base):
    def test_default_user_agent_has_no_email(self):
        ua = vr.make_request("https://api.crossref.org/works").get_header("User-agent")
        self.assertEqual(ua, vr.USER_AGENT)
        self.assertNotIn("@", ua)
        self.assertNotIn("mailto", ua)

    def test_mailto_only_when_given(self):
        net = self.net([])
        vr.check_entry(vr.parse_entry(f"Wibowo, A. (2020). {TITLE_A}. J. https://doi.org/{DOI_A}"), {})
        self.assertFalse(any("mailto" in u for u in net.urls))
        net = self.net([])
        vr.SETTINGS["mailto"] = "someone@example.org"
        cache = {}
        vr.check_entry(vr.parse_entry(f"Wibowo, A. (2020). {TITLE_A}. J. https://doi.org/{DOI_A}"), cache)
        self.assertTrue(any("mailto=someone%40example.org" in u for u in net.urls if u.startswith(vr.CROSSREF)))
        self.assertFalse(any("mailto" in k for k in cache))


class Main(Base):
    def run_main(self, text, *args, name="naskah.md"):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            out, js = os.path.join(d, "r.md"), os.path.join(d, "r.json")
            with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                code = vr.main([p, "--out", out, "--json", js, "--delay", "0", *args])
            report, data = "", []
            if os.path.exists(out):
                with open(out, encoding="utf-8") as f:
                    report = f.read()
            if os.path.exists(js):
                with open(js, encoding="utf-8") as f:
                    data = json.load(f)
        return code, report, data

    def test_exit_0_when_clean(self):
        self.net([(f"{vr.CROSSREF}/works/", crossref_work(TITLE_A, 2020, "Wibowo", DOI_A))])
        code, report, data = self.run_main(MANUSCRIPT)
        self.assertEqual(code, 0)
        self.assertEqual([r["status"] for r in data], ["verified", "not_checkable_online"])
        self.assertIn("| verified | 1 |", report)

    def test_exit_1_on_mismatch(self):
        self.net([(f"{vr.CROSSREF}/works/", crossref_work("Unrelated work on glaciers", 2020, "Berg", DOI_A))])
        code, report, _ = self.run_main(MANUSCRIPT)
        self.assertEqual(code, 1)
        self.assertIn("doi_mismatch (heavy)", report)

    def test_exit_2_without_heading(self):
        code, _, _ = self.run_main("# Intro\n\nNo references.\n")
        self.assertEqual(code, 2)

    def test_offline_makes_no_requests(self):
        net = self.net([])
        code, _, data = self.run_main(MANUSCRIPT, "--offline")
        self.assertEqual(code, 0)
        self.assertEqual(net.urls, [])
        self.assertEqual([r["status"] for r in data], ["unchecked", "not_checkable_online"])

    def test_cache_reused(self):
        net = self.net([(f"{vr.CROSSREF}/works/", crossref_work(TITLE_A, 2020, "Wibowo", DOI_A))])
        with tempfile.TemporaryDirectory() as d:
            cache = os.path.join(d, "c.json")
            self.run_main(MANUSCRIPT, "--cache", cache)
            first = len(net.urls)
            self.run_main(MANUSCRIPT, "--cache", cache)
            self.assertEqual(len(net.urls), first)


if __name__ == "__main__":
    unittest.main()
