"""Map what a revision touched, and find values the author changed in some places but not others.

A revision changes a number in Results and leaves the old one in the Abstract; renames a method
in Methods and keeps the old name in the Discussion. Reviewers catch this late and journals
catch it at proofs. This script compares the manuscript before and after revision and reports:

  1. values (numbers with a decimal point or %, integers of two or more digits other than years,
     and acronym-like terms such as OLS, AUROC, XGBoost) that the author swapped in place for
     another value, yet that still appear elsewhere — likely stale restatements;
  2. declared changes (--change OLD=NEW, repeatable): every line that still contains OLD;
  3. which sections were edited and which were not, so re-running roles know where to look.

Each argument is a review workspace (made by prepare_review.py) or a Markdown file.

    python impact_review.py review/2026-09-28 review/2026-10-15
    python impact_review.py old.md new.md --change "OLS=SEM" --change "0.81=0.78"

Writes <new>/impact.md when <new> is a workspace, otherwise prints the report.
Exit status 1 if a stale candidate or a surviving declared OLD value is found, 0 otherwise.
"""

import difflib
import os
import re
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from prepare_review import bagian  # noqa: E402

ANGKA = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?(?![\w])")
ISTILAH = re.compile(r"\b[A-Za-z0-9-]*[A-Z][A-Za-z0-9-]*[A-Z][A-Za-z0-9-]*\b")
AKHIR = re.compile(r"^#+\s*(references|daftar pustaka|bibliography|acknowledg|ucapan terima kasih)", re.I)


def muat(p):
    if os.path.isdir(p):
        p = os.path.join(p, "manuscript.md")
    with open(p, encoding="utf-8") as f:
        return f.read().splitlines()


def batas_badan(baris):
    """Lines after the reference list are not claims; their numbers (volumes, pages) are noise."""
    for no, b in enumerate(baris):
        if AKHIR.match(b):
            return no
    return len(baris)


def nilai(b):
    if b.startswith("#"):  # heading numbers ("## 2.1 …") are structure, not values
        b = re.sub(r"^#+\s*[\d.]*", "", b)
    hasil = []
    for m in ANGKA.findall(b):
        polos = m.rstrip("%")
        if "." in polos or "," in polos or m.endswith("%"):
            hasil.append(m)
        elif len(polos) >= 2 and not re.fullmatch(r"(19|20)\d\d", polos):
            hasil.append(m)
    hasil += [t for t in ISTILAH.findall(b) if sum(c.isupper() for c in t) >= 2 and not t.isdigit()]
    return hasil


def hitung(baris):
    c = Counter()
    for b in baris[:batas_badan(baris)]:
        c.update(nilai(b))
    return c


def substitusi(a, b):
    """Values in `a` that the word-level diff shows were swapped for another value in `b`.

    A rewritten paragraph drops and adds many terms; counting them flags noise. Only a short
    in-place swap ("81%" -> "78%", "OLS" -> "SEM") says the quantity or the method itself
    changed, so only those are kept."""
    wa, wb = a.split(), b.split()
    hasil = set()
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
        if op == "replace" and i2 - i1 <= 3 and j2 - j1 <= 3:
            lama, baru = set(nilai(" ".join(wa[i1:i2]))), set(nilai(" ".join(wb[j1:j2])))
            if lama and baru:
                hasil |= lama - baru
    return hasil


def seksi_untuk(no, seksi):
    kandidat = [s for s in seksi if s["start"] <= no <= s["end"]]
    return kandidat[-1]["title"] if kandidat else "(before first heading)"


def mengandung(b, t):
    return re.search(r"(?<![\w.])" + re.escape(t) + r"(?![\w])", b) is not None


def main(argv):
    ubah = []
    sisa = []
    i = 0
    while i < len(argv):
        if argv[i] == "--change" and i + 1 < len(argv) and "=" in argv[i + 1]:
            ubah.append(tuple(argv[i + 1].split("=", 1)))
            i += 2
        else:
            sisa.append(argv[i])
            i += 1
    if len(sisa) != 2:
        print(__doc__)
        return 2
    lama, baru = muat(sisa[0]), muat(sisa[1])
    seksi = bagian(baru)
    batas = batas_badan(baru)

    disunting = Counter()
    diganti = set()  # values the author substituted inside an edited passage
    sm = difflib.SequenceMatcher(None, lama, baru, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("replace", "insert"):
            for no in range(j1 + 1, j2 + 1):
                disunting[seksi_untuk(no, seksi)] += 1
        elif op == "delete":
            disunting[seksi_untuk(max(j1, 1), seksi)] += 1
        if op == "replace" and i1 < batas_badan(lama):
            diganti |= substitusi(" ".join(lama[i1:i2]), " ".join(baru[j1:j2]))

    c0, c1 = hitung(lama), hitung(baru)
    basi = sorted(t for t in diganti if 0 < c1[t] < c0[t])
    hilang = sorted(t for t in c0 if c1[t] == 0)
    muncul = sorted(t for t in c1 if c0[t] == 0)

    def lokasi(t):
        return [(no, seksi_untuk(no, seksi)) for no, b in enumerate(baru[:batas], 1) if mengandung(b, t)]

    L = [f"# Revision impact: {sisa[0]} -> {sisa[1]}", ""]
    masalah = 0
    if ubah:
        L += ["## Declared changes", ""]
        for old, new in ubah:
            tinggal = lokasi(old)
            masalah += bool(tinggal)
            L.append(f"- `{old}` -> `{new}`: "
                     + (f"OLD still at {', '.join(f'L{n} ({s})' for n, s in tinggal)}" if tinggal
                        else "OLD no longer appears")
                     + f"; NEW at {len(lokasi(new))} line(s)")
        L.append("")
    L += [f"## Changed in some places, still present in others ({len(basi)})", "",
          "Each of these was swapped for another value in at least one place but still appears "
          "elsewhere. Check every remaining occurrence: a stale restatement, or a different "
          "quantity that happens to share the value?", ""]
    for t in basi:
        L.append(f"- `{t}` ({c0[t]} -> {c1[t]}): "
                 + ", ".join(f"L{n} ({s})" for n, s in lokasi(t)))
    masalah += len(basi)
    L += ["", "## Sections edited", "", "| Section | Lines changed |", "|---|---|"]
    for s in seksi:
        if disunting[s["title"]]:
            L.append(f"| {s['title']} | {disunting[s['title']]} |")
    tidak = [s["title"] for s in seksi if not disunting[s["title"]]]
    if tidak:
        L += ["", "Not edited: " + "; ".join(tidak) + ". A claim restated here from an edited "
              "section did not change with it."]
    if hilang:
        L += ["", f"## Removed everywhere ({len(hilang)})", "", ", ".join(f"`{t}`" for t in hilang)]
    if muncul:
        L += ["", f"## New in this version ({len(muncul)})", "", ", ".join(f"`{t}`" for t in muncul)]
    teks = "\n".join(L) + "\n"

    if os.path.isdir(sisa[1]):
        keluar = os.path.join(sisa[1], "impact.md")
        with open(keluar, "w", encoding="utf-8") as f:
            f.write(teks)
        print(f"{len(basi)} value(s) changed in some places but not others, "
              f"{sum(1 for s in seksi if disunting[s['title']])} of {len(seksi)} sections edited\n"
              f"report: {keluar}")
    else:
        sys.stdout.write(teks)
    return 1 if masalah else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
