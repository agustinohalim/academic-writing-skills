"""Prepare an audit workspace for a thesis (skripsi, tesis, or disertasi).

Accepts Markdown or Word (.docx, converted with the standard library: headings from Heading /
Judul styles or from "BAB I" and "1.2 Title" lines, lists, tables). PDF is not read; convert it
first. The workspace holds everything the audit needs, so every finding can be traced to a line:

    <out>/manuscript.md            the thesis as audited (frozen; same name as manuscript-review,
                                   so impact_review.py can compare two drafts)
    <out>/manuscript_numbered.md   same text with L0001| prefixes
    <out>/sections.json            heading -> line range and kind (rumusan, tujuan, metode, ...)
    <out>/chain.json               items under problem statement, objectives, hypotheses, conclusions
    <out>/machine.json             deterministic findings (see below)
    <out>/meta.json                source, SHA-256, level, language, word count
    <out>/AUDIT.md                 the modules to run and the file to write

Machine checks — HEAVY ones must be fixed before a human reads the draft closely:
    CHAIN      numbered problem statements, objectives and conclusions differ in count (heavy)
    CITATIONS  author-year citations (et al., dkk., dan, &) missing from the reference list, and
               entries never cited (heavy)
    FIGURES    Tabel/Gambar/Table/Figure N or N.M captioned but never referred to, or referred to
               without a caption (heavy)
    NUMBERS    numbers in the abstract that never appear in the body (heavy)
    MARKERS    leftover placeholders (heavy)
    STRUCTURE  expected parts not found (light: headings may just be named differently)

Usage:
    python prepare_audit.py skripsi_budi.docx --level skripsi --out audit/budi/2026-10-01
    python prepare_audit.py Disertasi.md --level disertasi --out audit/2027-03-01 --lang en
    add --force to replace an existing workspace
"""

import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from modul import LEVELS, MODULES, WAJIB, jenis_judul, modul_untuk, nama_modul  # noqa: E402

PENANDA = re.compile(r"⬜|\bTODO\b|\[PERLU[^\]]*\]|\bXX+\b|\?\?\?|\[CITATION|\[(?:sitasi|citation) needed\]", re.I)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


# ---------------------------------------------------------------- conversion

def paragraf_docx(p):
    teks = "".join(t.text or "" for t in p.iter(W + "t")).strip()
    if not teks:
        return ""
    gaya, daftar = "", False
    ppr = p.find(W + "pPr")
    if ppr is not None:
        s = ppr.find(W + "pStyle")
        gaya = (s.get(W + "val") or "") if s is not None else ""
        daftar = ppr.find(W + "numPr") is not None
    m = re.search(r"(?:heading|judul)\s*(\d)", gaya, re.I)
    if m:
        return "#" * min(int(m.group(1)), 4) + " " + teks + "\n"
    if gaya.lower() == "title" or (re.match(r"BAB\s+[IVX]+\b", teks) and len(teks) < 80):
        return "# " + teks + "\n"
    # "1.2 Rumusan Masalah" typed by hand, without a heading style
    m = re.match(r"(\d+(?:\.\d+){1,2})\s+[A-Z]", teks)
    if m and len(teks) < 90 and not teks.endswith("."):
        return "#" * (m.group(1).count(".") + 1) + " " + teks + "\n"
    # "DAFTAR PUSTAKA", "ABSTRAK": short, all capitals
    if len(teks) < 40 and teks.isupper() and re.fullmatch(r"[A-Z\s&-]+", teks):
        return "# " + teks + "\n"
    if daftar:
        return "- " + teks
    return teks + "\n"


def docx_ke_md(jalur):
    with zipfile.ZipFile(jalur) as z:
        akar = ET.fromstring(z.read("word/document.xml"))
    keluar = []
    for el in akar.find(W + "body"):
        if el.tag == W + "p":
            keluar.append(paragraf_docx(el))
        elif el.tag == W + "tbl":
            keluar.append("")
            for i, tr in enumerate(el.iter(W + "tr")):
                sel = [" ".join((t.text or "") for t in tc.iter(W + "t")).strip().replace("|", "/")
                       for tc in tr.findall(W + "tc")]
                keluar.append("| " + " | ".join(sel) + " |")
                if i == 0:
                    keluar.append("|" + "---|" * len(sel))
            keluar.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(keluar)).strip() + "\n"


# ---------------------------------------------------------------- structure

def bagian(baris):
    hasil, kini = [], None
    for no, b in enumerate(baris, 1):
        if b.startswith("#"):
            if kini:
                kini["end"] = no - 1
                hasil.append(kini)
            judul = b.lstrip("#").strip()
            kini = {"title": judul, "level": len(b) - len(b.lstrip("#")), "start": no,
                    "kind": jenis_judul(judul)}
    if kini:
        kini["end"] = len(baris)
        hasil.append(kini)
    # a subsection with no kind of its own inherits its chapter's ("4.2 Pengujian" under Bab IV)
    induk = {}
    for s in hasil:
        for lv in [k for k in induk if k >= s["level"]]:
            del induk[lv]
        if not s["kind"]:
            atas = [induk[k] for k in sorted(induk) if induk[k]["kind"]]
            if atas and atas[-1]["kind"] in ("pendahuluan", "pustaka", "metode", "hasil", "penutup", "rujukan"):
                s["kind"] = atas[-1]["kind"]
        induk[s["level"]] = s
    return hasil


# one or two digits only: a wrapped line that starts "2001) and ..." is not a list item
BUTIR = re.compile(r"\s*(?:[-*•]|\d{1,2}[.)]|\(\d{1,2}\)|[a-z][.)]|H\d+\s*[:.])\s+(.*)")


def butir_seksi(baris, s):
    """Items under a section: list items if there are any, otherwise paragraphs."""
    isi = baris[s["start"]:s["end"]]
    daftar, par, paragraf = [], [], []
    for off, b in enumerate(isi, s["start"] + 1):
        m = BUTIR.match(b)
        if m and m.group(1).strip():
            daftar.append({"line": off, "text": m.group(1).strip()})
        elif daftar and b.startswith("  ") and b.strip():
            daftar[-1]["text"] += " " + b.strip()  # wrapped list item
        if b.strip() and not b.lstrip().startswith(("|", ">")):
            if not par:
                paragraf.append({"line": off, "text": ""})
            par.append(b.strip())
            paragraf[-1]["text"] = " ".join(par)
        else:
            par = []
    if daftar:
        return "list", daftar
    return "paragraph", paragraf


def rantai(baris, seksi):
    hasil = {}
    for k in ("rumusan", "tujuan", "hipotesis", "kesimpulan"):
        # "BAB V KESIMPULAN DAN SARAN" and "5.1 Kesimpulan" both match; the one with content wins
        for s in [x for x in seksi if jenis_judul(x["title"]) == k]:
            bentuk, butir = butir_seksi(baris, s)
            if butir:
                hasil[k] = {"section": s["title"], "line": s["start"], "form": bentuk, "items": butir}
                break
    return hasil


def paragraf(baris, seksi):
    """(line, text, kind) per paragraph; wrapped lines joined, list items and table rows apart."""
    jenis_baris = {}
    for s in seksi:
        for no in range(s["start"], s["end"] + 1):
            jenis_baris[no] = s["kind"]
    hasil, par, awal = [], [], 0

    def tutup():
        if par:
            hasil.append((awal, " ".join(x.strip() for x in par), jenis_baris.get(awal, "")))
        par.clear()

    for no, b in enumerate(baris, 1):
        if b.startswith("#") or not b.strip() or b.lstrip().startswith(">") or b.strip() == "---":
            tutup()
            continue
        if (BUTIR.match(b) or b.lstrip().startswith(("|", "![")) or
                re.match(r"[*_]+(Tabel|Gambar|Table|Fig)", b.strip())):
            tutup()
        elif jenis_baris.get(no) == "rujukan" and not b[:1].isspace():
            tutup()
        if not par:
            awal = no
        par.append(b)
        if b.lstrip().startswith("|"):
            tutup()
    tutup()
    return hasil


# ---------------------------------------------------------------- machine checks

def pesan(bahasa, id_, en):
    return id_ if bahasa == "id" else en


def periksa_rantai(ch, bahasa):
    daftar = {k: v for k, v in ch.items() if k in ("rumusan", "tujuan", "kesimpulan") and v["form"] == "list"}
    if len(daftar) < 2:
        return []
    jumlah = {k: len(v["items"]) for k, v in daftar.items()}
    if len(set(jumlah.values())) == 1:
        return []
    rinci = ", ".join(f"{k} {n}" for k, n in jumlah.items())
    no = min(v["line"] for v in daftar.values())
    return [(no, "heavy", pesan(bahasa,
             f"jumlah butir tidak sama ({rinci}): setiap rumusan masalah perlu tujuan dan kesimpulan yang menjawabnya",
             f"item counts differ ({rinci}): each research question needs an objective and a conclusion that answers it"))]


SITASI_KURUNG = re.compile(r"[(\[]([^()\[\]]*?\b(?:19|20)\d\d[a-z]?[^()\[\]]*)[)\]]")
NAMA = r"[A-Z][\w'’\-]+"
# "Wu et al. 2018", "Wu, et al. 2018", "Suboh, et al., 2019", "Zipes & Wellens, 1998"
PENGGAL = re.compile(rf"({NAMA}(?:\s{NAMA})?)(?:,?\s(?:and|&|dan)\s{NAMA}|,?\s(?:et al\.?|dkk\.?))?,?\s((?:19|20)\d\d[a-z]?)")
NARASI = re.compile(rf"\b({NAMA}(?:\s(?:and|&|dan)\s{NAMA}|\s(?:et al\.?|dkk\.?))?)\s[(\[]((?:19|20)\d\d[a-z]?)[)\],;:]")
BUKAN_NAMA = set("""January February March April May June July August September October November December
Januari Februari Maret Mei Juni Juli Agustus Oktober Desember Accessed Diakses Table Tabel Tables Fig
Figure Gambar Section Bab Version Versi Release Tahun Year No Nomor UU Pasal University Universitas
Institute Institut College Faculty Fakultas Department Jurusan Program Programme""".split())
# "Surname, A.", "Surname AB", "Sugiyono. (2019)": a name, then initials or the year
AWAL_ENTRI = re.compile(r"(?:(?:de|van|den|der|von|da|di|du|le|la|dos|del)\s)*[A-ZÀ-ɏ][\wÀ-ɏ'’\-]+"
                        r"(?:\s[A-ZÀ-ɏ][\wÀ-ɏ'’\-]+)?(?:,|\s[A-Z]\.|\s[A-Z]{1,3}\b|\.?\s*\(?(?:19|20)\d\d)")


def periksa_sitasi(par, bahasa):
    badan = [(n, t) for n, t, k in par if k not in ("rujukan", "abstrak")]
    rujukan = [(n, t) for n, t, k in par if k == "rujukan"]
    if not rujukan:
        return []
    kutip = {}
    for no, b in badan:
        for isi in SITASI_KURUNG.findall(b):
            for bag in isi.split(";"):
                m = PENGGAL.search(bag)
                if m:
                    kutip.setdefault((m.group(1).split()[-1], m.group(2)), no)
        for nama, th in NARASI.findall(b):
            kutip.setdefault((nama.split()[0], th), no)
    kutip = {k: v for k, v in kutip.items() if k[0] not in BUKAN_NAMA and not any(c.isdigit() for c in k[0])}
    entri = []
    for no, b in rujukan:
        s = b.strip().lstrip("-*0123456789.[] ").strip()
        th = re.search(r"\b((?:19|20)\d\d[a-z]?)\b", s)
        # organisations as authors ("Task Force of the ... (1996)") have no initials
        if s and th and (AWAL_ENTRI.match(s) or re.match(r"[A-Z].{0,150}\((?:19|20)\d\d", s)):
            entri.append((no, s, th.group(1)))
    temuan, dipakai = [], set()
    for (nama, th), no in sorted(kutip.items(), key=lambda x: x[1]):
        cocok = [i for i, (_, s, t) in enumerate(entri) if t == th and nama.lower() in s[:150].lower()]
        if not cocok:
            temuan.append((no, "heavy", pesan(bahasa, f"sitasi '{nama} {th}' tidak ada di daftar pustaka",
                                              f"citation '{nama} {th}' has no reference entry")))
        dipakai.update(cocok)
    for i, (no, s, _) in enumerate(entri):
        if i not in dipakai:
            temuan.append((no, "heavy", pesan(bahasa, f"entri pustaka tidak pernah disitasi: {s[:70]}…",
                                              f"reference entry never cited: {s[:70]}…")))
    return temuan


LABEL = r"(Tabel|Gambar|Table|Fig(?:ure)?\.?)\s+(\d+(?:\.\d+)?)"
KETERANGAN = re.compile(r"[*_]*" + LABEL + r"\s*[.:*]?")
RUJUK = re.compile(r"\b" + LABEL, re.I)  # "pada tabel 3.3" in running text is lower case


EN = {"Tabel": "Table", "Gambar": "Figure"}


def jenis_label(j):
    return "Tabel" if j.lower().startswith("tab") else "Gambar"


def periksa_gambar(par, bahasa):
    ada, dirujuk, ganda = {}, {}, []
    for no, t, k in par:
        if k == "rujukan":
            continue
        teks = t.strip()
        gambar_md = re.match(r"!\[([^\]]*)\]", teks)  # ![Fig. 1 Caption](file.png)
        if gambar_md:
            teks = "*" + gambar_md.group(1)  # an image's alt text is a caption
        m = KETERANGAN.match(teks)
        # "**Tabel 3.1** Kebutuhan", "Tabel 3.1. Kebutuhan", "Tabel 3.1 Kebutuhan" are captions;
        # "Tabel 3.1 memuat ..." / "Table 1 shows ..." are sentences that refer to the table
        sesudah = teks[m.end():].lstrip(" *_") if m else ""
        # a bold/italic label, or a label followed by "." ":" "–", is a caption at any length;
        # a bare label followed by a capitalised word only when short
        berformat = teks[:1] in "*_" or re.match(r"\S+\s+\d+(?:\.\d+)*\s*[.:–-](?!\d)", teks)
        if m and (berformat or (len(teks) <= 200 and sesudah[:1].isupper())):
            kunci = (jenis_label(m.group(1)), m.group(2))
            if kunci in ada:
                ganda.append((no, kunci, ada[kunci]))
            ada.setdefault(kunci, no)
            teks = teks[m.end():]
        for mm in RUJUK.finditer(teks):
            sekitar = teks[max(0, mm.start() - 30):mm.end() + 30]
            if re.search(r"et al\.?|dkk\.?|\btheir\b|\bmereka\b|\((?:[^()]*\s)?(?:19|20)\d\d[a-z]?\)", sekitar):
                continue  # a table in a cited work
            dirujuk.setdefault((jenis_label(mm.group(1)), mm.group(2)), no)
    temuan = []
    for k, no in dirujuk.items():
        if k not in ada:
            temuan.append((no, "heavy", pesan(bahasa, f"{k[0]} {k[1]} dirujuk tetapi tidak ada keterangannya",
                                              f"{EN[k[0]]} {k[1]} is referred to but has no caption")))
    for k, no in ada.items():
        if k not in dirujuk:
            temuan.append((no, "heavy", pesan(bahasa, f"{k[0]} {k[1]} tidak pernah dirujuk di teks",
                                              f"{EN[k[0]]} {k[1]} is never referred to in the text")))
    for no, k, pertama in ganda:
        temuan.append((no, "heavy", pesan(bahasa, f"nomor {k[0]} {k[1]} dipakai dua kali (juga di L{pertama})",
                                          f"{EN[k[0]]} {k[1]} is numbered twice (also at L{pertama})")))
    return temuan


ANGKA = re.compile(r"(?<![\w.,])[−-]?\d+(?:[.,]\d+)?%?")


def periksa_angka(par, bahasa):
    abstrak = [(n, t) for n, t, k in par if k == "abstrak"]
    badan = " ".join(t for _, t, k in par if k not in ("abstrak", "rujukan")).replace("−", "-")
    temuan = []
    for no, b in abstrak:
        for a in ANGKA.findall(b):
            inti = a.replace("−", "-").lstrip("-")
            if re.fullmatch(r"(19|20)\d\d", inti) or re.fullmatch(r"\d", inti):
                continue
            # an English abstract writes 96.67 where the Indonesian body writes 96,67
            tukar = inti.translate(str.maketrans(".,", ",."))
            if inti not in badan and tukar not in badan:
                temuan.append((no, "heavy", pesan(bahasa, f"angka '{a}' di abstrak tidak muncul di badan naskah",
                                                  f"number '{a}' in the abstract does not appear in the body")))
    return temuan


def periksa_struktur(seksi, level, bahasa):
    ada = {s["kind"] for s in seksi}
    if "penutup" in ada:
        ada.add("kesimpulan")
    kurang = [k for k in WAJIB if k not in ada]
    return [(0, "light", pesan(bahasa, f"bagian tidak ditemukan: {k} (mungkin judulnya lain)",
                               f"part not found: {k} (the heading may be named differently)")) for k in kurang]


def periksa_penanda(baris, bahasa):
    return [(no, "heavy", pesan(bahasa, f"penanda tertinggal: {m.group(0)}", f"leftover placeholder: {m.group(0)}"))
            for no, b in enumerate(baris, 1) if not b.lstrip().startswith(">")
            for m in [PENANDA.search(b)] if m]


def tebak_bahasa(teks):
    t = teks.lower()
    id_ = sum(t.count(w) for w in ("pendahuluan", "daftar pustaka", "kesimpulan", "penelitian ini", " yang "))
    en = sum(t.count(w) for w in ("introduction", "references", "conclusion", "this study", " the "))
    return "id" if id_ >= en / 3 else "en"


# ---------------------------------------------------------------- main

def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    opsi = {}
    for k in ("--out", "--level", "--lang"):
        if k in argv:
            i = argv.index(k)
            opsi[k] = argv[i + 1]
            del argv[i:i + 2]
    if len(argv) != 1 or "--out" not in opsi or opsi.get("--level") not in LEVELS:
        print(__doc__)
        return 2
    src, out, level = argv[0], opsi["--out"], opsi["--level"]
    if os.path.exists(out):
        if not force:
            print(f"{out} exists; use --force to replace it")
            return 2
        shutil.rmtree(out)

    if src.lower().endswith(".docx"):
        teks = docx_ke_md(src)
    elif src.lower().endswith((".md", ".txt")):
        with open(src, encoding="utf-8") as f:
            teks = f.read()
    else:
        print("only .md, .txt and .docx are read; convert PDF to .docx or .md first")
        return 2
    bahasa = opsi.get("--lang") or tebak_bahasa(teks)
    baris = teks.splitlines()
    seksi = bagian(baris)
    ch = rantai(baris, seksi)
    par = paragraf(baris, seksi)

    mesin = (periksa_rantai(ch, bahasa) + periksa_sitasi(par, bahasa) + periksa_gambar(par, bahasa)
             + periksa_angka(par, bahasa) + periksa_penanda(baris, bahasa)
             + periksa_struktur(seksi, level, bahasa))
    mesin = [{"line": n, "weight": w, "message": m} for n, w, m in sorted(mesin, key=lambda x: (x[1] != "heavy", x[0]))]

    os.makedirs(os.path.join(out))
    with open(os.path.join(out, "manuscript.md"), "w", encoding="utf-8") as f:
        f.write(teks)
    with open(os.path.join(out, "manuscript_numbered.md"), "w", encoding="utf-8") as f:
        for no, b in enumerate(baris, 1):
            f.write(f"L{no:04d}| {b}\n")
    for nama, isi in (("sections.json", seksi), ("chain.json", ch), ("machine.json", mesin)):
        with open(os.path.join(out, nama), "w", encoding="utf-8") as f:
            json.dump(isi, f, ensure_ascii=False, indent=1)
    meta = {"source": os.path.abspath(src), "sha256": hashlib.sha256(teks.encode("utf-8")).hexdigest(),
            "level": level, "lang": bahasa, "lines": len(baris), "words": len(teks.split()),
            "modules": modul_untuk(level)}
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    with open(os.path.join(out, "AUDIT.md"), "w", encoding="utf-8") as f:
        f.write(f"# Audit: {level}\n\nRead `manuscript_numbered.md`, `chain.json` and `machine.json`, then write "
                "`audit.json` in the schema of `references/audit-schema.md`, covering every module below "
                "exactly once. Then run `report_audit.py` on this folder.\n\n| ID | Module |\n|---|---|\n")
        for m in MODULES:
            if level in m[3]:
                f.write(f"| {m[0]} | {nama_modul(m[0], bahasa)} |\n")

    berat = sum(1 for m in mesin if m["weight"] == "heavy")
    print(f"workspace: {out}\n  {level}, language {bahasa}, {meta['words']} words, {len(seksi)} headings\n"
          f"  chain: " + ", ".join(f"{k} {len(v['items'])} ({v['form']})" for k, v in ch.items()) +
          f"\n  machine findings: {berat} heavy, {len(mesin) - berat} light\n"
          f"  next: write {out}/audit.json (AUDIT.md), then report_audit.py {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
