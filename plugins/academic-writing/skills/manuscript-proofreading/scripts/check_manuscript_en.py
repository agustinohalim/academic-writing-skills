"""Checks an English-language journal manuscript written in Markdown before submission.

Five things a machine can decide:

  NUMBERS   numbers in the Abstract that never appear in the body
  CITATIONS author-year citations with no reference entry, and entries never cited
  FIGURES   Fig./Table cited without a caption, or captioned but never cited
  MARKERS   leftover placeholders: ⬜, TODO, [PERLU ...], XX, ???, [CITATION
  STYLE     machine-prose vocabulary, em-dash density, the "X, not Y" tic, short punchline sentences

The first four are HEAVY and make the script exit with status 1. STYLE findings are LIGHT:
read them one by one, some are fine as written.

Conventions it expects: "## Abstract", "## References" (or Bibliography), optionally
"## Figure captions"; captions start with "Fig. N." / "**Table N.**". Blockquote lines (">")
are skipped, so editorial notes can live there. Author-year styles (APA, Harvard, Springer
"Surname AB (2021)") and [Surname, 2021] brackets are recognised; numeric styles are not.

Usage:
    python check_manuscript_en.py manuscript.md [more.md ...]
    python check_manuscript_en.py --heavy manuscript.md        # hide style findings
    python check_manuscript_en.py --no-markers manuscript.md   # drafts: placeholders not heavy
"""

import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Words that in a research paper almost always signal machine prose. Kept short on purpose:
# words that are also legitimate technical terms (robust, significant) are left out.
KATA_MESIN = [
    "delve", "delves", "delving", "crucial", "crucially", "notably", "underscore",
    "underscores", "underscoring", "landscape", "pivotal", "intricate", "intricacies",
    "showcase", "showcases", "showcasing", "leverage", "leverages", "leveraging",
    "seamless", "seamlessly", "tapestry", "realm", "paramount", "holistic",
    "groundbreaking", "cutting-edge", "game-changer", "shed light", "sheds light",
    "a testament to", "it is worth noting", "it is important to note", "in today's",
    "navigate the", "unlock", "unlocks", "harness the", "multifaceted", "meticulous",
    "meticulously", "commendable", "embark",
]

PENANDA = re.compile(r"⬜|\bTODO\b|\[PERLU[^\]]*\]|\bXX+\b|\?\?\?|\[CITATION")


def baca(jalur):
    with open(jalur, encoding="utf-8") as f:
        return f.read().splitlines()


def bagian(baris):
    """Pecah naskah menjadi abstract, badan, referensi, keterangan gambar.

    Setiap unsur adalah (no_baris_awal, paragraf). Baris yang dibungkus digabung dulu,
    karena sitasi dan kalimat sering terpotong di ujung baris. Butir daftar ("- ") dan
    baris tabel ("|") masing-masing jadi paragraf sendiri. Kutipan ">" dilewati.
    """
    kelompok = {"abstrak": [], "badan": [], "rujukan": [], "keterangan": []}
    kini, par, awal = "kepala", [], 0

    def tutup():
        if par and kini in kelompok:
            kelompok[kini].append((awal, " ".join(x.strip() for x in par)))
        par.clear()

    for no, b in enumerate(baris, 1):
        judul = b.strip().lower()
        if judul.startswith("#"):
            tutup()
            if judul.startswith("## "):
                if "abstract" in judul:
                    kini = "abstrak"
                elif "reference" in judul or "bibliography" in judul:
                    kini = "rujukan"
                elif "caption" in judul:
                    kini = "keterangan"
                else:
                    kini = "badan"
            continue
        if not b.strip() or b.lstrip().startswith(">") or b.strip() == "---":
            tutup()
            continue
        if re.match(r"\s*([-*]|\d+\.)\s|\s*\||\s*\*\*(Fig|Table)", b):
            tutup()
        elif kini == "rujukan" and not b[:1].isspace():
            # daftar pustaka satu entri per baris: baris tak menjorok selalu entri baru
            tutup()
        if not par:
            awal = no
        par.append(b)
        if b.lstrip().startswith("|"):
            tutup()
    tutup()
    return kelompok["abstrak"], kelompok["badan"], kelompok["rujukan"], kelompok["keterangan"]


ANGKA = re.compile(r"(?<![\w.])[−-]?\d+(?:[.,]\d+)?%?")


def periksa_angka(abstrak, badan, keterangan):
    teks_badan = " ".join(b for _, b in badan + keterangan).replace("−", "-")
    temuan = []
    for no, b in abstrak:
        for a in ANGKA.findall(b):
            a = a.replace("−", "-")
            inti = a.lstrip("-")
            # tahun, bilangan satu digit, dan angka bulat kecil terlalu umum untuk dicek
            if re.fullmatch(r"(19|20)\d\d", inti) or re.fullmatch(r"\d", inti):
                continue
            if inti not in teks_badan:
                temuan.append((no, f"number '{a}' in the Abstract does not appear in the body"))
    return temuan


SITASI_KURUNG = re.compile(r"[(\[]([^()\[\]]*?\b(?:19|20)\d\d[a-z]?[^()\[\]]*)[)\]]")
SITASI_NARASI = re.compile(
    r"\b([A-Z][\w'’\-]+(?:\s(?:and|&)\s[A-Z][\w'’\-]+|\set al\.)?)\s[(\[]((?:19|20)\d\d[a-z]?)[)\],;]")
PENGGAL = re.compile(
    r"([A-Z][\w'’\-]+(?:\s[A-Z][\w'’\-]+)?)(?:\s(?:and|&)\s[A-Z][\w'’\-]+|\set al\.)?,?\s((?:19|20)\d\d[a-z]?)")
# kata berhuruf kapital di depan tahun yang bukan nama penulis
BUKAN_NAMA = set("""January February March April May June July August September October
November December Accessed Table Tables Fig Figure Section Version Release""".split())
PARTIKEL = r"(?:(?:de|van|den|der|von|da|di|du|le|la|dos|del)\s)*"
# awal entri pustaka: "Surname, A." (APA/Harvard) atau "Surname AB" (Springer)
AWAL_ENTRI = re.compile(PARTIKEL + r"[A-ZÀ-ɏ][\wÀ-ɏ'’\-]+(?:\s[A-ZÀ-ɏ][\wÀ-ɏ'’\-]+)?(?:,|\s[A-Z]{1,4}\b)")


def sitasi_teks(badan):
    """Kembalikan {(nama_belakang, tahun): no_baris} dari sitasi author-year."""
    hasil = {}

    def catat(nama, th, no):
        if nama in BUKAN_NAMA or any(c.isdigit() for c in nama):
            return
        hasil.setdefault((nama, th), no)

    for no, b in badan:
        for isi in SITASI_KURUNG.findall(b):
            for bag in isi.split(";"):
                m = PENGGAL.search(bag)
                if m:
                    catat(m.group(1).split()[-1], m.group(2), no)
        for nama, th in SITASI_NARASI.findall(b):
            catat(nama.split()[0], th, no)
    return hasil


def entri_rujukan(rujukan):
    entri = []
    for no, b in rujukan:
        s = b.strip().lstrip("-*0123456789. ").strip()
        # pengarang lembaga ("Task Force of ... (1996)") tidak berpola nama orang
        if not s or not (AWAL_ENTRI.match(s) or re.match(r"[A-Z].{0,150}\((?:19|20)\d\d", s)):
            continue
        th = re.search(r"\b((?:19|20)\d\d[a-z]?)\b", s)
        entri.append((no, s, th.group(1) if th else None))
    return entri


def periksa_sitasi(badan, rujukan):
    if not rujukan:
        return []
    kutip = sitasi_teks(badan)
    entri = entri_rujukan(rujukan)
    temuan = []
    dipakai = set()
    for (nama, th), no in sorted(kutip.items(), key=lambda x: x[1]):
        cocok = [i for i, (_, s, t) in enumerate(entri)
                 if t == th and nama.lower() in s[:120].lower()]
        if not cocok:
            temuan.append((no, f"citation '{nama} {th}' has no entry in References"))
        dipakai.update(cocok)
    for i, (no, s, t) in enumerate(entri):
        if i not in dipakai and t:
            temuan.append((no, f"reference entry never cited: {s[:70]}…"))
    return temuan


KETERANGAN = re.compile(r"[*_]*(Fig(?:ure)?\.?|Table)\s+(\d+)\s*[.:*]")
RUJUK_GAMBAR = re.compile(r"\b(Fig(?:ure)?s?\.?|Tables?)\s+(\d+)(?:\s*(?:[–-]|and|to)\s*(\d+))?")


def periksa_gambar(badan, keterangan):
    """Paragraf yang diawali "Fig. N." / "**Table N.**" adalah keterangan; sisanya rujukan."""
    dirujuk, ada = {}, {}
    for no, b in badan + keterangan:
        teks = b.strip()
        m = KETERANGAN.match(teks)
        if m:
            j = "Table" if m.group(1).startswith("Tab") else "Fig"
            ada.setdefault((j, m.group(2)), no)
            teks = teks[m.end():]
        for jenis, n1, n2 in RUJUK_GAMBAR.findall(teks):
            j = "Table" if jenis.startswith("Tab") else "Fig"
            for n in range(int(n1), int(n2 or n1) + 1):
                dirujuk.setdefault((j, str(n)), no)
    temuan = []
    for k, no in dirujuk.items():
        if k not in ada:
            temuan.append((no, f"{k[0]} {k[1]} is cited but has no caption"))
    for k, no in ada.items():
        if k not in dirujuk:
            temuan.append((no, f"{k[0]} {k[1]} has a caption but is never cited in the text"))
    return temuan


def periksa_penanda(baris):
    return [(no, f"leftover placeholder: {m.group(0)}")
            for no, b in enumerate(baris, 1) if not b.lstrip().startswith(">")
            for m in [PENANDA.search(b)] if m]


def periksa_gaya(abstrak, badan):
    temuan = []
    isi = abstrak + badan
    kata_total = 0
    em = 0
    for no, b in isi:
        if b.lstrip().startswith(("|", "```")) or KETERANGAN.match(b.strip()):
            continue
        kata_total += len(b.split())
        em += b.count("—")
        rendah = b.lower()
        for k in KATA_MESIN:
            if re.search(rf"\b{re.escape(k)}\b", rendah):
                temuan.append((no, f"machine-prose vocabulary: '{k}'"))
        if re.search(r",\s+not\s+\w+", b):
            temuan.append((no, "'X, not Y' pattern: forced contrast; consider stating it directly"))
        for kal in re.split(r"(?<=[.!?])\s+", b.strip()):
            n = len(kal.split())
            if 2 <= n <= 5 and kal.endswith(".") and not re.search(r"\d|et al|Fig|Table", kal):
                temuan.append((no, f"short punchline sentence: '{kal}'"))
    if kata_total:
        per_seribu = em * 1000 / kata_total
        if per_seribu > 4:
            temuan.append((0, f"em dash {per_seribu:.1f} per 1,000 words (guide: ≤ 4)"))
    rather = sum(b.lower().count("rather than") for _, b in isi)
    if kata_total and rather * 1000 / kata_total > 1.5:
        temuan.append((0, f"'rather than' {rather} times: repeated contrast pattern"))
    return temuan


MSG = {
    "judul": "title frames a local case ('evidence from', 'case study'): reviewers read it as local interest; state the general finding",
    "abs_kata": "abstract has {} words (most journals: 150-250)",
    "abs_angka": "abstract carries {} numbers: reads as a list of findings, not one arc (aim for <= 4)",
    "kontribusi": "{} contribution items: more than 4 suggests several papers in one; pick the central one",
    "angka_baru": "number '{}' in Discussion/Conclusion does not appear earlier: new result in the Discussion?",
    "baca_panjang": "sentences average {:.1f} words, {:.0f}% over 35 words (aim: average <= 22, long < 10%) - automated language scores penalise this most",
    "baca_angka": "{:.0f}% of sentences carry 4+ numbers: move numbers to tables, keep one or two per sentence",
    "baca_hubung": "{:.1f} hyphenated compounds per 1,000 words (guide <= {}): noun stacks such as 'per-district rolling-origin test folds' are hard to parse; unpack some into phrases",
    "baca_kurung": "{:.1f} parentheses per 1,000 words (guide <= {}): parenthetical asides interrupt sentences",
    "baca_titikkoma": "{:.1f} semicolons per 1,000 words (guide <= {}): split into sentences",
    "baca_kalimat": "long or number-dense sentence ({} words): '{}...'",
    "baca_jamak": "'{}': uncountable noun used as countable (e.g. research -> studies, information -> details)",
    "ing_rider": "', highlighting/underscoring/reflecting …' rider: state the consequence as its own clause with a subject",
    "kopula": "'serves as / stands as a …': write 'is'",
    "hedge": "stacked hedge ('may potentially'): one hedge is enough",
    "not_only": "'not only … but also': usually a staged contrast; state both points plainly",
    "overclaim": "overstatement (prove, definitively, guarantee, universally, highly significant): size the verb to the evidence",
}


# Patterns from the "signs of AI writing" taxonomy used by blader/humanizer (MIT), limited to the
# ones that are wrong in research prose: -ing riders, copula avoidance, stacked hedges.
POLA_AI = [
    (r",\s+(?:highlighting|underscoring|emphasi[sz]ing|showcasing|reflecting|illustrating|demonstrating|signal(?:l)?ing)\b", "ing_rider"),
    (r"\b(?:serves|stands|acts|functions) as (?:a|an|the)\b", "kopula"),
    (r"\b(?:may|might|could) (?:potentially|possibly|perhaps)\b|\bpotentially (?:may|might|could)\b", "hedge"),
    (r"\bnot only\b[^.]{0,80}\bbut also\b", "not_only"),
    # overstatement list adapted from K-Dense scientific-writing lint_manuscript.py (MIT, K-Dense Inc.)
    (r"\b(?:proves?|proven|definitively|guarantees?|no limitations|universally|highly significant)\b", "overclaim"),
]


def periksa_pola_ai(abstrak, badan):
    temuan = []
    for no, b in abstrak + badan:
        for pola, kunci in POLA_AI:
            if re.search(pola, b, re.IGNORECASE):
                temuan.append((no, MSG[kunci]))
    return temuan


UNCOUNTABLE = ["researches", "informations", "equipments", "literatures", "evidences",
               "softwares", "feedbacks", "knowledges", "datas", "advices", "trainings",
               "infrastructures", "furnitures", "works done", "a research ", "an evidence",
               "a software", "an information"]


def periksa_keterbacaan(abstrak, badan):
    """Readability signals that automated language-quality scores penalise. All LIGHT."""
    temuan = []
    paragraf = [(no, b) for no, b in abstrak + badan
                if not b.lstrip().startswith(("|", "```", "-", "*", "1.", "2.", "3."))
                and not KETERANGAN.match(b.strip())]
    kalimat = []
    for no, b in paragraf:
        b2 = re.sub(r"`[^`]*`", "X", b)
        b2 = re.sub(r"\([^()]*\b(?:19|20)\d\d[a-z]?\b[^()]*\)", "", b2)
        for k in re.split(r"(?<=[.!?])\s+(?=[A-Z])", b2):
            if len(k.split()) > 2:
                kalimat.append((no, k))
    if not kalimat:
        return temuan
    kata = sum(len(k.split()) for _, k in kalimat)
    panjang = [(no, k) for no, k in kalimat if len(k.split()) > 35]
    rata = kata / len(kalimat)
    if rata > 24 or len(panjang) / len(kalimat) > 0.10:
        temuan.append((0, MSG["baca_panjang"].format(rata, len(panjang) * 100 / len(kalimat))))
    padat = [(no, k) for no, k in kalimat if len(re.findall(r"\d+(?:\.\d+)?", k)) >= 4]
    if len(padat) / len(kalimat) > 0.10:
        temuan.append((0, MSG["baca_angka"].format(len(padat) * 100 / len(kalimat))))
    teks = " ".join(k for _, k in kalimat)
    for kunci, pola, batas in (("baca_hubung", r"\b[A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*\b", 15),
                               ("baca_kurung", r"\(", 8), ("baca_titikkoma", r";", 5)):
        n = len(re.findall(pola, teks)) * 1000 / kata
        if n > batas:
            temuan.append((0, MSG[kunci].format(n, batas)))
    terburuk = sorted(panjang + padat, key=lambda x: -len(x[1].split()))
    dilihat = set()
    for no, k in terburuk:
        if no in dilihat or len(dilihat) >= 8:
            continue
        dilihat.add(no)
        temuan.append((no, MSG["baca_kalimat"].format(len(k.split()), k[:90])))
    rendah = teks.lower()
    for u in UNCOUNTABLE:
        for m in re.finditer(r"\b" + re.escape(u.strip()) + r"\b", rendah):
            no = next((n for n, k in kalimat if u.strip() in k.lower()), 0)
            temuan.append((no, MSG["baca_jamak"].format(u.strip())))
            break
    return temuan


def periksa_struktur(baris):
    """Structure-level signals that drive novelty/presentation scores. All LIGHT."""
    temuan = []
    judul = next((b for b in baris if b.startswith("# ")), "")
    if re.search(r"(?i)evidence from|a case study|case study of|: the case of", judul):
        temuan.append((1, MSG["judul"]))
    bagian_kini, isi = "", {}
    for no, b in enumerate(baris, 1):
        if b.startswith("## "):
            bagian_kini = b[3:].strip().lower()
            continue
        if b.lstrip().startswith(">"):
            continue
        isi.setdefault(bagian_kini, []).append((no, b))
    abstrak = next((v for k, v in isi.items() if "abstract" in k), [])
    teks_abs = " ".join(b for _, b in abstrak)
    kata = len(teks_abs.split())
    if kata > 250:
        temuan.append((abstrak[0][0], MSG["abs_kata"].format(kata)))
    angka = [a for a in ANGKA.findall(teks_abs) if not re.fullmatch(r"(19|20)\d\d|\d", a.lstrip("-−"))]
    if len(angka) > 6:
        temuan.append((abstrak[0][0], MSG["abs_angka"].format(len(angka))))
    for k, v in isi.items():
        if "introduction" not in k:
            continue
        for i, (no, b) in enumerate(v):
            if re.search(r"(?i)contribution", b):
                butir = [x for x in v[i + 1:i + 40] if re.match(r"\s*\d+\.\s", x[1])]
                if len(butir) > 4:
                    temuan.append((no, MSG["kontribusi"].format(len(butir))))
                break
    hasil = " ".join(b for k, v in isi.items() if not re.search(r"discussion|conclusion|abstract|reference", k)
                     for _, b in v).replace("−", "-")
    for k, v in isi.items():
        if not re.search(r"discussion|conclusion", k):
            continue
        for no, b in v:
            for a in ANGKA.findall(b):
                inti = a.replace("−", "-").lstrip("-")
                if "." in inti and inti not in hasil:
                    temuan.append((no, MSG["angka_baru"].format(a)))
    return temuan

def periksa(jalur, hanya_berat=False, penanda=True):
    baris = baca(jalur)
    abstrak, badan, rujukan, keterangan = bagian(baris)
    berat = (periksa_angka(abstrak, badan, keterangan) + periksa_sitasi(badan, rujukan)
             + periksa_gambar(badan, keterangan) + (periksa_penanda(baris) if penanda else []))
    ringan = [] if hanya_berat else periksa_gaya(abstrak, badan) + periksa_struktur(baris) + periksa_keterbacaan(abstrak, badan) + periksa_pola_ai(abstrak, badan)
    nama = jalur
    print(f"\n== {nama}: {len(berat)} heavy, {len(ringan)} light")
    for no, pesan in sorted(berat):
        print(f"  HEAVY  L{no}: {pesan}")
    for no, pesan in sorted(ringan):
        print(f"  light  L{no}: {pesan}")
    return len(berat)


def main(argv):
    hanya_berat = "--heavy" in argv
    penanda = "--no-markers" not in argv
    jalur = [a for a in argv if a not in ("--heavy", "--no-markers")]
    if not jalur:
        print(__doc__)
        return 2
    total = sum(periksa(j, hanya_berat, penanda) for j in jalur)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
