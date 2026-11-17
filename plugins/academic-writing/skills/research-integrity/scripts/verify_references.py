"""Checks that every entry in a reference list exists, and that its DOI belongs to it.

An entry cited from memory fails in one of three ways: the work does not exist, the DOI points to
a different paper, or the metadata (year, first author) drifted. This script looks each entry up
in Crossref and OpenAlex and reports one status per entry:

  verified              DOI resolves; title, year and first author agree with the record
  partial               DOI resolves to the right work, but year (often online-first vs print)
                        or first author differs; the differing fields are listed
  doi_mismatch          DOI resolves to a DIFFERENT work. The key integrity failure (HEAVY)
  doi_not_found         DOI in neither Crossref nor OpenAlex. Typo, or an invented DOI (HEAVY)
  found                 no DOI given; a matching record was found. Its DOI is a suggestion:
                        open it, verify, then add it yourself. Nothing is written to the manuscript
  not_found             no DOI given and no confident match. Not proof the work is fake: many
                        Indonesian journals are not in Crossref/OpenAlex. Check by hand
  not_checkable_online  book, thesis, regulation, web page or dataset without a DOI. These do
                        not normally have one; the route to verify them is listed instead
  unchecked             --offline: parsed and classified only
  error                 network failure; run again

Exit status 1 when any entry is doi_mismatch or doi_not_found, 2 on usage errors, else 0.

GARUDA (garuda.kemdiktisaintek.go.id) and SINTA (sinta.kemdiktisaintek.go.id) have no public
API, so for Indonesian entries the script prints the exact title to paste into their search
boxes; that check is manual. It does not build deep search links: their URL formats could not be
verified.

A verified or found status means the work exists and the metadata matches. It does not mean the
source says what the manuscript claims it says; that needs the source itself.

Input: Markdown, plain text, .docx (read with the standard library), or BibTeX (.bib). The
reference list is the section under a heading such as Daftar Pustaka, Referensi, References,
Bibliography, or Works Cited (the last one in the file, so a table of contents does not count);
--all takes the whole file. One entry per paragraph, or per line when entries are not separated
by blank lines.

Network etiquette: a fixed User-Agent naming this script, about 0.3 s between requests, one retry
on 429/5xx. No e-mail address is sent unless you pass --mailto (Crossref polite pool). An OpenAlex
key can be given with --openalex-key or OPENALEX_API_KEY.

Usage:
    python verify_references.py naskah.md
    python verify_references.py skripsi.docx --out cek_pustaka.md --json cek_pustaka.json
    python verify_references.py refs.bib --cache .refcache.json
    python verify_references.py naskah.md --offline          # parse and classify only
    python verify_references.py daftar.txt --all             # the whole file is the list
"""

import argparse
import datetime
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

USER_AGENT = ("academic-writing-skills-verify-references/1.0 "
              "(+https://github.com/agustinohalim/academic-writing-skills)")
CROSSREF = "https://api.crossref.org"
OPENALEX = "https://api.openalex.org"
GARUDA = "https://garuda.kemdiktisaintek.go.id/"
SINTA = "https://sinta.kemdiktisaintek.go.id/"

SETTINGS = {"mailto": None, "openalex_key": None, "delay": 0.3, "timeout": 20}
_LAST_REQUEST = [0.0]

HEAVY = ("doi_mismatch", "doi_not_found")
ORDER = ("doi_mismatch", "doi_not_found", "partial", "not_found", "error", "found", "verified",
         "not_checkable_online", "unchecked")

MATCH, CLEARLY_DIFFERENT = 0.85, 0.60


# ---------------------------------------------------------------- network

class NetworkError(Exception):
    pass


def make_request(url):
    return urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                "Accept": "application/json"})


def fetch_json(url):
    """GET url and return parsed JSON; None on 404. Raises NetworkError otherwise.

    Every HTTP call in this script goes through here (tests replace it)."""
    for attempt in (0, 1):
        wait = SETTINGS["delay"] - (time.monotonic() - _LAST_REQUEST[0])
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST[0] = time.monotonic()
        try:
            with urllib.request.urlopen(make_request(url), timeout=SETTINGS["timeout"]) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == 0 and (e.code == 429 or e.code >= 500):
                retry = e.headers.get("Retry-After") if e.headers else None
                time.sleep(min(float(retry), 30) if retry and retry.isdigit() else 3)
                continue
            raise NetworkError(f"HTTP {e.code} for {url}") from e
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            if attempt == 0:
                time.sleep(2)
                continue
            raise NetworkError(f"{type(e).__name__}: {e}") from e
    raise NetworkError(f"no response for {url}")


def _get(base, params, cache):
    """Cached GET. The cache key never contains the mailto address or the API key."""
    key = base + ("?" + urllib.parse.urlencode(sorted(params.items())) if params else "")
    if cache is not None and key in cache:
        return cache[key]
    full = dict(params)
    if base.startswith(CROSSREF) and SETTINGS["mailto"]:
        full["mailto"] = SETTINGS["mailto"]
    if base.startswith(OPENALEX) and SETTINGS["openalex_key"]:
        full["api_key"] = SETTINGS["openalex_key"]
    url = base + ("?" + urllib.parse.urlencode(full) if full else "")
    data = fetch_json(url)
    if cache is not None:
        cache[key] = data
    return data


def crossref_by_doi(doi, cache):
    data = _get(f"{CROSSREF}/works/{urllib.parse.quote(doi, safe='/:;()')}", {}, cache)
    return record_crossref(data.get("message")) if data else None


def openalex_by_doi(doi, cache):
    data = _get(f"{OPENALEX}/works/doi:{urllib.parse.quote(doi, safe='/:;()')}", {}, cache)
    return record_openalex(data) if data else None


def crossref_search(text, cache):
    data = _get(f"{CROSSREF}/works", {"query.bibliographic": text[:400], "rows": "2"}, cache)
    items = ((data or {}).get("message") or {}).get("items") or []
    return [record_crossref(i) for i in items]


def openalex_search(title, cache):
    data = _get(f"{OPENALEX}/works", {"search": title[:300], "per_page": "3"}, cache)
    return [record_openalex(i) for i in (data or {}).get("results") or []]


def record_crossref(m):
    if not m:
        return None
    year = None
    for k in ("issued", "published-print", "published-online", "created"):
        parts = ((m.get(k) or {}).get("date-parts") or [[None]])[0]
        if parts and parts[0]:
            year = int(parts[0])
            break
    fam = [a.get("family") or a.get("name") or "" for a in m.get("author") or []]
    return {"source": "Crossref", "title": " ".join(m.get("title") or []).strip(),
            "year": year, "families": [f for f in fam if f], "doi": (m.get("DOI") or "").lower(),
            "venue": " ".join(m.get("container-title") or []).strip(), "type": m.get("type") or ""}


def record_openalex(w):
    if not w:
        return None
    fam = []
    for a in w.get("authorships") or []:
        name = ((a.get("author") or {}).get("display_name") or "").strip()
        if name:
            fam.append(name.split()[-1])
    doi = (w.get("doi") or "").lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    venue = (((w.get("primary_location") or {}).get("source")) or {}).get("display_name") or ""
    return {"source": "OpenAlex", "title": (w.get("display_name") or w.get("title") or "").strip(),
            "year": w.get("publication_year"), "families": fam, "doi": doi, "venue": venue}


# ---------------------------------------------------------------- reading

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text:
            continue
        style = p.find(f"{W}pPr/{W}pStyle")
        val = (style.get(W + "val") or "") if style is not None else ""
        if re.search(r"heading|judul|title", val, re.I):
            m = re.search(r"(\d)", val)
            text = "#" * (int(m.group(1)) if m else 1) + " " + text
        out.append(text)
    return "\n\n".join(out)


REF_HEADING = re.compile(
    r"^(?:bab\s+[ivx]+\s+)?(?:daftar\s+pustaka|daftar\s+referensi|daftar\s+rujukan|referensi|"
    r"rujukan|kepustakaan|bibliografi|references?|reference\s+list|bibliography|works\s+cited|"
    r"literature\s+cited|sources\s+cited)\s*:?$", re.I)
END_HEADING = re.compile(r"^(?:lampiran|appendix|appendices|riwayat\s+hidup|biodata|"
                         r"about\s+the\s+authors?|author\s+biograph)", re.I)
MD_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def heading_text(line):
    s = re.sub(r"^#{1,6}\s*", "", line.strip())
    s = re.sub(r"[*_`]", "", s).strip()
    return re.sub(r"^(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s+", "", s).strip()


def find_section(text):
    """Lines of the last reference-list section, or None."""
    lines = text.splitlines()
    start, level = None, 1
    for i, line in enumerate(lines):
        m = MD_HEADING.match(line.strip())
        cand = heading_text(line)
        if cand and REF_HEADING.match(cand) and (m or len(line.strip()) < 40):
            start, level = i, (len(m.group(1)) if m else 1)
    if start is None:
        return None
    out = []
    for line in lines[start + 1:]:
        m = MD_HEADING.match(line.strip())
        if m and len(m.group(1)) <= level:
            break
        if END_HEADING.match(heading_text(line)) and (m or len(line.strip()) < 40):
            break
        if m:          # a sub-heading inside the list ("## Buku") separates entries
            out.append("")
            continue
        out.append(line)
    return out


MARKER = re.compile(r"^\s*(?:[-*+•]|\d{1,3}[.)]|\[\d{1,3}\])\s+")
YEAR_RE = re.compile(r"(?<![\d/.])(?:19|20)\d\d(?![\d/])")
AUTHOR_START = re.compile(
    r"^(?:(?:de|van|den|der|von|da|di|du|le|la|dos|del|al|el)\s)*[A-ZÀ-Ý][\w'’\-À-ɏ]+"
    r"(?:\s[A-ZÀ-Ý][\w'’\-À-ɏ]+)*,\s?[A-ZÀ-Ý]"
    r"|^(?:[A-Z]\.\s?)+(?:-[A-Z]\.\s?)?[A-ZÀ-Ý][\w'’\-]+,")


def _starts_entry(line, prev):
    if MARKER.match(line):
        return True
    if not prev or line[:1].isspace():
        return False
    s = line.strip()
    if not prev.rstrip().endswith((".", ")", "]")) and not re.search(r"(doi\.org/|https?://)\S+$", prev):
        return False
    if not s[:1].isupper():
        return False
    return bool(AUTHOR_START.match(s) or YEAR_RE.search(s[:80]))


def split_entries(lines):
    entries, cur = [], []
    for raw in lines:
        if not raw.strip():
            if cur:
                entries.append(" ".join(cur))
                cur = []
            continue
        if cur and _starts_entry(raw, cur[-1]):
            entries.append(" ".join(cur))
            cur = []
        cur.append(raw.strip())
    if cur:
        entries.append(" ".join(cur))
    out = []
    for e in entries:
        e = MARKER.sub("", e).strip()
        e = re.sub(r"\s+", " ", e)
        if len(e) >= 20 and re.search(r"[A-Za-z]{3}", e):
            out.append(e)
    return out


# ---------------------------------------------------------------- BibTeX

def parse_bib(text):
    entries, i = [], 0
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]*)\s*,", text[at:])
        if not m:
            i = at + 1
            continue
        kind = m.group(1).lower()
        if kind in ("comment", "string", "preamble"):
            i = at + m.end()
            continue
        j, fields = at + m.end(), {}
        while j < len(text):
            fm = re.match(r"\s*([\w\-]+)\s*=\s*", text[j:])
            if not fm:
                break
            name, j = fm.group(1).lower(), j + fm.end()
            if text[j] == "{":
                depth, k = 0, j
                while k < len(text):
                    depth += {"{": 1, "}": -1}.get(text[k], 0)
                    if depth == 0:
                        break
                    k += 1
                value, j = text[j + 1:k], k + 1
            elif text[j] == '"':
                k = text.find('"', j + 1)
                value, j = text[j + 1:k], k + 1
            else:
                vm = re.match(r"[^,}\s]+", text[j:])
                value, j = (vm.group(0), j + vm.end()) if vm else ("", j)
            fields[name] = re.sub(r"[{}]", "", re.sub(r"\s+", " ", value)).strip()
            cm = re.match(r"\s*,", text[j:])
            if not cm:
                break
            j += cm.end()
        entries.append(bib_entry(kind, fields))
        i = j
    return entries


BIB_TYPE = {"book": "book", "inbook": "book", "incollection": "book", "booklet": "book",
            "phdthesis": "thesis", "mastersthesis": "thesis", "thesis": "thesis",
            "online": "web", "electronic": "web", "www": "web", "dataset": "dataset",
            "article": "article", "inproceedings": "article", "conference": "article",
            "proceedings": "article"}


def bib_entry(kind, f):
    authors = f.get("author", "")
    first = authors.split(" and ")[0].strip()
    family = first.split(",")[0].strip() if "," in first else (first.split()[-1] if first else "")
    venue = f.get("journal") or f.get("booktitle") or f.get("publisher") or f.get("school") or ""
    text = f"{authors} ({f.get('year', 'n.d.')}). {f.get('title', '')}. {venue}."
    if f.get("doi"):
        text += f" https://doi.org/{f['doi']}"
    ym = YEAR_RE.search(f.get("year", ""))
    typ = BIB_TYPE.get(kind, "unknown")
    if typ == "unknown" and f.get("url") and not venue:
        typ = "web"
    return {"text": text, "doi": clean_doi(f.get("doi", "")) or None,
            "year": int(ym.group(0)) if ym else None, "author": family,
            "title": f.get("title", ""), "type": typ}


# ---------------------------------------------------------------- parsing an entry

DOI_RE = re.compile(r"(?:https?://(?:dx\.)?doi\.org/|\bdoi:\s*|\bDOI:?\s*)?(10\.\d{4,9}/[^\s\"<>]+)", re.I)
URL_RE = re.compile(r"https?://\S+")


def clean_doi(doi):
    doi = doi.strip()
    while doi and doi[-1] in ".,;:]>'\"*_":
        doi = doi[:-1]
    while doi.endswith(")") and doi.count(")") > doi.count("("):
        doi = doi[:-1]
    return doi.lower()


def strip_md(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return re.sub(r"(?<!\w)[*_]+|[*_]+(?!\w)", "", s).replace("<", "").replace(">", "")


TITLE_PATTERNS = [
    re.compile(r"[“\"]([^”\"]{8,}?)[,.]?[”\"]"),
    re.compile(r"\((?:19|20)\d\d[a-z]?(?:,[^)]*)?\)\.?\s+(.{8,}?[?!]?)(?:[.?!](?:\s|$))"),
    re.compile(r"(?<![\d/])(?:19|20)\d\d[a-z]?\.\s+(.{8,}?[?!]?)(?:[.?!](?:\s|$))"),
]

KIND = [
    ("regulation", re.compile(r"\b(?:undang-undang|uu\s+(?:no|nomor)|peraturan|permen\w*|perpres|"
                              r"perda|keputusan\s+(?:menteri|presiden|direktur)|surat\s+edaran|"
                              r"regulation\s+\(|act\s+of\s+\d{4}|directive\s+\d)", re.I)),
    ("thesis", re.compile(r"\b(?:skripsi|tesis|disertasi|tugas\s+akhir|thesis|dissertation|"
                          r"doctoral|master'?s)\b", re.I)),
    ("dataset", re.compile(r"\b(?:\[?data\s?set\]?|zenodo|figshare|dryad|kaggle|dataverse)\b", re.I)),
]
JOURNALISH = re.compile(r"\b(?:jurnal|journal|proceedings?|prosiding|conference|konferensi|"
                        r"seminar|transactions|review|letters|vol\.|volume)\b|\d+\s?\(\d+\)", re.I)
BOOKISH = re.compile(r"\b(?:penerbit|press|publisher|publishing|publications|edisi|edition|ed\.|"
                     r"\(eds?\.\)|cetakan|rineka|alfabeta|erlangga|andi\s+offset|deepublish|"
                     r"rajawali|kencana|bumi\s+aksara|remaja\s+rosdakarya|wiley|mcgraw|pearson|"
                     r"prentice|sage|routledge|cengage|o'reilly)\b"
                     r"|\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?:\s?[A-Z][\w.&\s]{2,40}\.?\s*$", re.I)
WEBISH = re.compile(r"\b(?:diakses|accessed|retrieved|tersedia\s+(?:di|pada)|available\s+(?:at|from)|"
                    r"dari\s+https?://)", re.I)
INDONESIAN = re.compile(r"\b(?:jurnal|prosiding|universitas|institut|politeknik|sekolah\s+tinggi|"
                        r"skripsi|tesis|disertasi|dkk\.?|penerbit|kementerian|badan|seminar\s+nasional|"
                        r"indonesia|nusantara|teknologi|pendidikan|penelitian|pengaruh|terhadap|analisis)\b",
                        re.I)


def classify(text, doi):
    journal = JOURNALISH.search(text)
    for kind, rx in KIND:
        # an article titled "Implementasi Peraturan ..." is still an article
        if rx.search(text) and (kind == "dataset" or not journal):
            return kind
    if journal:
        return "article"
    if BOOKISH.search(text):
        return "book"
    if URL_RE.search(text) and (WEBISH.search(text) or not doi):
        return "web"
    return "unknown"


def first_author(text):
    s = MARKER.sub("", strip_md(text)).strip()
    m = re.match(r"^((?:[A-Z]\.\s?)+(?:-[A-Z]\.\s?)?)([A-ZÀ-Ý][\w'’\-À-ɏ]+)", s)
    if m:
        return m.group(2)
    lead = re.split(r"[,(]|\.\s", s, maxsplit=1)[0].strip()
    return lead if 0 < len(lead.split()) <= 4 else (lead.split()[0] if lead else "")


def parse_entry(text):
    m = DOI_RE.search(text)
    doi = clean_doi(m.group(1)) if m else None
    bare = URL_RE.sub(" ", DOI_RE.sub(" ", text))
    yp = re.search(r"\(((?:19|20)\d\d)[a-z]?(?:,[^)]*)?\)", bare)
    ym = yp or YEAR_RE.search(bare)
    year = int(ym.group(1) if yp else ym.group(0)) if ym else None
    title = ""
    plain = strip_md(bare)
    for rx in TITLE_PATTERNS:
        tm = rx.search(plain)
        if tm:
            title = tm.group(1).strip(" .,")
            break
    return {"text": text, "doi": doi, "year": year, "author": first_author(text),
            "title": title or plain.strip(), "type": classify(text, doi)}


# ---------------------------------------------------------------- comparison

def norm(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def title_similarity(entry, found_title):
    """Best of: guessed title vs record title, and how much of the record title the entry holds."""
    ft = norm(found_title)
    if not ft:
        return 0.0
    guess = norm(entry["title"])
    ratio = difflib.SequenceMatcher(None, guess, ft).ratio() if guess else 0.0
    words = [w for w in ft.split() if len(w) > 2] or ft.split()
    have = set(norm(entry["text"]).split())
    coverage = sum(w in have for w in words) / len(words)
    if len(words) < 3:          # very short titles: coverage alone proves little
        coverage = min(coverage, ratio)
    return max(ratio, coverage)


def author_agrees(entry, rec):
    if not rec["families"]:
        return None
    lead = norm(re.split(r"\((?:19|20)\d\d|(?<![\d/])(?:19|20)\d\d", entry["text"], maxsplit=1)[0][:200])
    fam = norm(rec["families"][0])
    if not fam:
        return None
    return any(part in lead.split() for part in fam.split() if len(part) > 1) or fam in lead


def compare(entry, rec):
    sim = title_similarity(entry, rec["title"])
    diffs = []
    if sim < MATCH:
        diffs.append(f"title similarity {sim:.2f}")
    if entry["year"] and rec["year"] and entry["year"] != rec["year"]:
        diffs.append(f"year {entry['year']} vs record {rec['year']}")
    a = author_agrees(entry, rec)
    if a is False:
        diffs.append(f"first author vs record '{rec['families'][0]}'")
    return sim, diffs


def acceptable(entry, rec):
    if not rec or not rec["title"]:
        return False
    sim, _ = compare(entry, rec)
    if sim < MATCH:
        return False
    if entry["year"] and rec["year"] and abs(entry["year"] - rec["year"]) > 1:
        return False
    return author_agrees(entry, rec) is not False


ROUTE = {
    "book": "publisher page or library catalogue (WorldCat, OPAC Perpusnas); check the title and copyright page",
    "thesis": "the university's institutional repository or library record",
    "regulation": "the official issuing body (JDIH, peraturan.go.id for Indonesian regulation) or official gazette",
    "web": "open the URL; record title, issuing body, date published and date accessed",
    "dataset": "the original repository: version, date, licence",
}


def manual_pointer(entry):
    t = entry["title"] if entry["title"] != entry["text"] else entry["text"][:160]
    return (f'Search the title "{t}" in GARUDA ({GARUDA}) and SINTA ({SINTA}), '
            f"or on the journal's own site (OJS archive). These portals have no public API.")


# ---------------------------------------------------------------- checking

def check_entry(entry, cache, offline=False):
    r = dict(entry, status="", found_title="", found_doi="", source="", note="", manual="")
    r["indonesian"] = bool(INDONESIAN.search(entry["text"]))
    if not entry["doi"] and entry["type"] in ROUTE:
        r["status"], r["note"] = "not_checkable_online", "verify via " + ROUTE[entry["type"]]
    elif offline:
        r["status"] = "unchecked"
    else:
        try:
            _check_online(r, cache)
        except NetworkError as e:
            r["status"], r["note"] = "error", str(e)
    if r["status"] == "not_found" or (r["indonesian"] and r["status"] in ("partial", "unchecked", "error")):
        r["manual"] = manual_pointer(entry)
    return r


NOTICE = re.compile(r"^\s*(correction|erratum|corrigendum|retraction|expression of concern)\b", re.I)


def rank(entry, rec):
    """Sort key for equally acceptable hits: a record whose DOI suffix or article number
    appears in the entry first (e078378 in the entry picks bmj-2023-078378), correction and
    retraction notices last, then the search engine's own order (sort is stable)."""
    text = re.sub(r"[^a-z0-9]", "", entry["text"].lower())
    tail = re.split(r"[./-]", rec.get("doi") or "")[-1]
    cited = bool(tail) and len(re.sub(r"\D", "", tail)) >= 4 and tail.lower() in text
    notice = rec.get("type") in ("correction", "erratum", "retraction") or bool(NOTICE.match(rec.get("title") or ""))
    return (not cited, notice)


def _fill(r, rec):
    r["found_title"], r["found_doi"], r["source"] = rec["title"], rec["doi"], rec["source"]


def _check_online(r, cache):
    if r["doi"]:
        rec = crossref_by_doi(r["doi"], cache) or openalex_by_doi(r["doi"], cache)
        if not rec:
            r["status"], r["note"] = "doi_not_found", "DOI not in Crossref or OpenAlex; check for a typo or an invented DOI"
            return
        _fill(r, rec)
        sim, diffs = compare(r, rec)
        if sim < CLEARLY_DIFFERENT:
            r["status"] = "doi_mismatch"
            r["note"] = f"the DOI belongs to a different work (title similarity {sim:.2f})"
        elif diffs:
            r["status"], r["note"] = "partial", "; ".join(diffs)
        else:
            r["status"] = "verified"
        return
    hits = [h for h in crossref_search(r["text"], cache) if h]
    good = [h for h in hits if acceptable(r, h)]
    if not good:
        hits = [h for h in openalex_search(r["title"], cache) if h]
        good = [h for h in hits if acceptable(r, h)]
    if not good:
        r["status"], r["note"] = "not_found", "no confident match in Crossref or OpenAlex"
        return
    good.sort(key=lambda h: rank(r, h))
    best = good[0]
    _fill(r, best)
    r["status"] = "found"
    notes = [f"suggested DOI {best['doi']}: open it, verify, then add" if best["doi"]
             else "record has no DOI"]
    _, diffs = compare(r, best)
    notes += diffs
    if len(good) > 1 and good[1]["doi"] and good[1]["doi"] != best["doi"]:
        notes.append(f"a second record also matches ({good[1]['doi']}): preprint or another version?")
    r["note"] = "; ".join(notes)


# ---------------------------------------------------------------- report

def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def report_md(path, results, offline):
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    today = datetime.date.today().isoformat()
    src = "parsed only (--offline)" if offline else "checked against Crossref and OpenAlex"
    out = [f"# Reference verification: {os.path.basename(path)}", "",
           f"{len(results)} entries, {src}, {today}.", "", "| Status | Count |", "|---|---|"]
    for s in ORDER:
        if counts.get(s):
            out.append(f"| {s}{' (heavy)' if s in HEAVY else ''} | {counts[s]} |")
    out += ["", "| # | First author | Year | Status | Found title / DOI | Note |",
            "|---|---|---|---|---|---|"]
    for r in results:
        found = r["found_title"] + (f" — {r['found_doi']}" if r["found_doi"] else "")
        if not found and r["doi"]:
            found = r["doi"]
        out.append(f"| {r['n']} | {cell(r['author'])} | {r['year'] or 'n.d.'} | {r['status']} | "
                   f"{cell(found)} | {cell(r['note'])} |")
    manual = [r for r in results if r["manual"]]
    if manual:
        out += ["", "## Manual checks", ""]
        out += [f"- [{r['n']}] {cell(r['manual'])}" for r in manual]
    out += ["", "## Reading the statuses", "",
            "- `doi_mismatch`, `doi_not_found`: fix before anything else; a DOI that belongs to another "
            "work, or to none, is the classic trace of a citation written from memory.",
            "- `partial`: the work is right, a field is not. Online-first and print years often differ "
            "by one; use the version you read.",
            "- `found`: the suggested DOI is a lead, not an answer. Open it and confirm it is the work you read.",
            "- `not_found`: not proof the work is fake. Many Indonesian journals are only in GARUDA or "
            "SINTA, or on their own OJS site.",
            "- `not_checkable_online`: books, theses, regulations, web pages and datasets without a DOI "
            "normally have none. Verify by the route given.",
            "- None of these statuses checks that the source supports the claim it is cited for."]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- main

def load_entries(path, whole):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bib":
        with open(path, encoding="utf-8") as f:
            return parse_bib(f.read())
    if ext == ".docx":
        text = docx_text(path)
    else:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    lines = text.splitlines() if whole else find_section(text)
    if lines is None:
        raise SystemExit(2)
    return [parse_entry(e) for e in split_entries(lines)]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify a reference list against Crossref and OpenAlex.")
    ap.add_argument("file")
    ap.add_argument("--all", action="store_true", help="treat the whole file as the reference list")
    ap.add_argument("--out", help="write the Markdown report here instead of stdout")
    ap.add_argument("--json", help="also write results as JSON")
    ap.add_argument("--cache", help="JSON cache of API responses, reused between runs")
    ap.add_argument("--offline", action="store_true", help="parse and classify only, no network")
    ap.add_argument("--mailto", help="contact e-mail for the Crossref polite pool (sent only if given)")
    ap.add_argument("--openalex-key", default=os.environ.get("OPENALEX_API_KEY"))
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between requests")
    ap.add_argument("--limit", type=int, help="check only the first N entries")
    a = ap.parse_args(argv)

    SETTINGS.update(mailto=a.mailto, openalex_key=a.openalex_key, delay=a.delay)
    if not os.path.isfile(a.file):
        print(f"not found: {a.file}", file=sys.stderr)
        return 2
    try:
        entries = load_entries(a.file, a.all)
    except SystemExit:
        print("No reference-list heading found (Daftar Pustaka, Referensi, References, Bibliography...). "
              "Add one, or pass --all if the file holds only the list.", file=sys.stderr)
        return 2
    if a.limit:
        entries = entries[:a.limit]
    if not entries:
        print("The reference list is empty.", file=sys.stderr)
        return 2

    cache = {}
    if a.cache and os.path.isfile(a.cache):
        with open(a.cache, encoding="utf-8") as f:
            cache = json.load(f)
    results = []
    for n, e in enumerate(entries, 1):
        r = check_entry(e, cache, offline=a.offline)
        r["n"] = n
        results.append(r)
    if a.cache:
        with open(a.cache, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)

    md = report_md(a.file, results, a.offline)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    heavy = sum(r["status"] in HEAVY for r in results)
    print(f"{len(results)} entries; {heavy} heavy (doi_mismatch / doi_not_found)", file=sys.stderr)
    return 1 if heavy else 0


if __name__ == "__main__":
    sys.exit(main())
