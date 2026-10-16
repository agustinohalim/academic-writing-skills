"""Prepare a review workspace for a Markdown manuscript.

Creates a folder the reviewer roles work in, so every finding can be traced to an exact line:

    <out>/manuscript.md            copy of the manuscript as reviewed (frozen)
    <out>/manuscript_numbered.md   same text with L0001| line prefixes, for citing lines
    <out>/sections.json            heading -> first/last line
    <out>/machine.json             deterministic findings from check_manuscript_en.py
    <out>/findings/                one <role>.json per reviewer (written by the reviewers)
    <out>/PANEL.md                 the roles to run and the file each must write
    <out>/journal_fit.md           copy of the target journal's fit evidence (--fit), if given

Usage:
    python prepare_review.py manuscript.md --out review/2026-09-28
    python prepare_review.py manuscript.md --out review/2026-09-28 --force   # replace
    python prepare_review.py manuscript.md --out review/2026-09-28 --fit Target_Journals.md

--fit names the file holding the fit test for the journal the paper is about to go to
(journal-targeting step 2: aims sentence, three recent similar papers, topic count). The editor
role judges fit against it; without it, fit is not assessable and the report says the paper is
not ready to submit.
"""

import hashlib
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "manuscript-proofreading", "scripts"))

ROLES = [
    ("editor", "Editor and journal fit — originality, significance, fit, the one-sentence contribution"),
    ("methods", "Methods and statistics — design, leakage, units, uncertainty, reproducibility"),
    ("domain", "Domain and literature — prior work, what is new relative to it, missing references"),
    ("presentation", "Presentation — structure, abstract arc, readability, figures and tables"),
    ("devils-advocate", "Devil's advocate — strongest counter-argument, overgeneralisation, the 'so what' test"),
]


def bagian(baris):
    hasil, kini = [], None
    for no, b in enumerate(baris, 1):
        if b.startswith("#"):
            if kini:
                kini["end"] = no - 1
                hasil.append(kini)
            kini = {"title": b.lstrip("#").strip(), "level": len(b) - len(b.lstrip("#")), "start": no}
    if kini:
        kini["end"] = len(baris)
        hasil.append(kini)
    return hasil


def main(argv):
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    fit = None
    if "--fit" in argv:
        i = argv.index("--fit")
        if i + 1 >= len(argv):
            print(__doc__)
            return 2
        fit = argv[i + 1]
        del argv[i:i + 2]
        if not os.path.isfile(fit):
            print(f"--fit: {fit} not found")
            return 2
    if "--out" not in argv or len(argv) < 3:
        print(__doc__)
        return 2
    out = argv[argv.index("--out") + 1]
    src = [a for i, a in enumerate(argv) if a != "--out" and (i == 0 or argv[i - 1] != "--out")][0]
    if os.path.exists(out):
        if not force:
            print(f"{out} exists; use --force to replace it")
            return 2
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "findings"))

    with open(src, encoding="utf-8") as f:
        teks = f.read()
    baris = teks.splitlines()
    shutil.copyfile(src, os.path.join(out, "manuscript.md"))
    with open(os.path.join(out, "manuscript_numbered.md"), "w", encoding="utf-8") as f:
        for no, b in enumerate(baris, 1):
            f.write(f"L{no:04d}| {b}\n")
    with open(os.path.join(out, "sections.json"), "w", encoding="utf-8") as f:
        json.dump(bagian(baris), f, ensure_ascii=False, indent=1)

    mesin = []
    try:
        import check_manuscript_en as cm
        berat, ringan = cm.temukan(src)
        mesin = ([{"line": n, "weight": "heavy", "message": m} for n, m in berat]
                 + [{"line": n, "weight": "light", "message": m} for n, m in ringan])
    except Exception as e:  # checker missing or manuscript without expected headings
        mesin = [{"line": 0, "weight": "light", "message": f"machine check not run: {e}"}]
    with open(os.path.join(out, "machine.json"), "w", encoding="utf-8") as f:
        json.dump(mesin, f, ensure_ascii=False, indent=1)
    if fit:
        shutil.copyfile(fit, os.path.join(out, "journal_fit.md"))

    meta = {
        "source": os.path.abspath(src),
        "sha256": hashlib.sha256(teks.encode("utf-8")).hexdigest(),
        "lines": len(baris),
        "words": len(teks.split()),
        "roles": [r for r, _ in ROLES],
        "journal_fit": os.path.abspath(fit) if fit else None,
    }
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)

    with open(os.path.join(out, "PANEL.md"), "w", encoding="utf-8") as f:
        f.write("# Review panel\n\nEach role reads `manuscript_numbered.md` independently, without "
                "seeing the other roles' files, and writes `findings/<role>.json` in the schema of "
                "`references/finding-schema.md`.\n\n| Role | File | Focus |\n|---|---|---|\n")
        for r, fokus in ROLES:
            f.write(f"| {r} | `findings/{r}.json` | {fokus} |\n")
        if fit:
            f.write("\nThe editor role also reads `journal_fit.md` (fit evidence for the target journal).\n")
        else:
            f.write("\nNo `journal_fit.md`: journal fit cannot be judged, and the report will mark the "
                    "manuscript not ready to submit. Re-run with `--fit <file>` once the target is chosen.\n")
        f.write("\nThen run `consolidate_review.py` on this folder.\n")

    berat_n = sum(1 for m in mesin if m["weight"] == "heavy")
    print(f"workspace: {out}\n  {meta['lines']} lines, {meta['words']} words, "
          f"{len(bagian(baris))} headings\n  machine findings: {berat_n} heavy, "
          f"{len(mesin) - berat_n} light\n  journal fit evidence: {'yes' if fit else 'NO (use --fit)'}\n  next: run the five roles (PANEL.md), then consolidate_review.py {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
