"""Consolidate a review panel's findings into one report.

Reads a workspace made by prepare_review.py after the reviewer roles have written
findings/<role>.json, then:

  1. validates every file against the schema (references/finding-schema.md);
  2. verifies each quote against the frozen manuscript and corrects its line number —
     findings whose quote is not in the manuscript are kept apart and do not count;
  3. clusters findings raised by several roles about the same passage (consensus);
  4. aggregates the seven dimension scores (median and spread; spread >= 2 = disagreement);
  5. applies the decision rules (references/decision-rules.md);
  6. writes report.md (for the author) and findings_final.json (for diff_review.py).

Usage:
    python consolidate_review.py review/2026-09-28
Exit status: 0 report written, 1 schema errors (report still written for valid files), 2 usage.
"""

import json
import os
import re
import statistics
import sys

DIMENSIONS = ["originality", "rigour", "evidence", "argument", "presentation", "literature", "significance"]
SEVERITIES = ["critical", "major", "minor"]
RANK = {s: i for i, s in enumerate(SEVERITIES)}


def normal(t):
    return re.sub(r"\s+", " ", t.replace("**", "").replace("`", "")).strip()


def muat(ws):
    with open(os.path.join(ws, "manuscript.md"), encoding="utf-8") as f:
        baris = f.read().splitlines()
    with open(os.path.join(ws, "sections.json"), encoding="utf-8") as f:
        seksi = json.load(f)
    mesin = []
    if os.path.exists(os.path.join(ws, "machine.json")):
        with open(os.path.join(ws, "machine.json"), encoding="utf-8") as f:
            mesin = json.load(f)
    return baris, seksi, mesin


def validasi(role, data):
    galat = []
    if not isinstance(data, dict):
        return [f"{role}: top level must be an object"]
    for k in ("role", "scores", "findings"):
        if k not in data:
            galat.append(f"{role}: missing '{k}'")
    for d, v in (data.get("scores") or {}).items():
        if d not in DIMENSIONS:
            galat.append(f"{role}: unknown dimension '{d}'")
        elif not isinstance(v, (int, float)) or not 1 <= v <= 5:
            galat.append(f"{role}: score for {d} must be 1-5")
    for i, t in enumerate(data.get("findings") or []):
        for k in ("title", "severity", "dimension", "quote", "problem", "fix"):
            if not t.get(k):
                galat.append(f"{role} finding {i + 1}: missing '{k}'")
        if t.get("severity") not in SEVERITIES:
            galat.append(f"{role} finding {i + 1}: severity must be one of {SEVERITIES}")
        if t.get("dimension") not in DIMENSIONS:
            galat.append(f"{role} finding {i + 1}: dimension must be one of {DIMENSIONS}")
    return galat


def verifikasi(temuan, baris):
    """Find the quote in the manuscript. Returns (verified, line)."""
    q = normal(temuan.get("quote", ""))
    if len(q) < 8:
        return False, temuan.get("line")
    target = temuan.get("line") or 0
    cocok = []
    # search single lines first, then paragraphs joined across wrapped lines
    for no, b in enumerate(baris, 1):
        if q in normal(b):
            cocok.append(no)
    if not cocok:
        # a quote spanning wrapped lines must start on the window's first line, so the
        # line number points at where the quote begins, not at an earlier line
        for no in range(1, len(baris) + 1):
            awal = normal(baris[no - 1])
            if not awal:
                continue
            jendela = normal(" ".join(baris[no - 1:no + 5]))
            i = jendela.find(q)
            if 0 <= i < len(awal):
                cocok.append(no)
    if not cocok:
        return False, temuan.get("line")
    return True, min(cocok, key=lambda n: abs(n - target))


def seksi_untuk(no, seksi):
    kandidat = [s for s in seksi if s["start"] <= (no or 0) <= s["end"]]
    return kandidat[-1]["title"] if kandidat else ""


def kata(t):
    return {w for w in re.findall(r"[a-z]{4,}", t.lower())}


def mirip(a, b):
    if a["line"] and b["line"] and abs(a["line"] - b["line"]) <= 3:
        qa, qb = normal(a["quote"]), normal(b["quote"])
        if qa in qb or qb in qa:
            return True
        ka, kb = kata(a["title"] + " " + a["problem"]), kata(b["title"] + " " + b["problem"])
        if ka and kb and len(ka & kb) / len(ka | kb) >= 0.25:
            return True
    return False


def klaster(temuan, gabungan=None):
    """Cluster findings. Automatic rule: same passage (mirip). Optional `gabungan` is a list of
    groups of "role:id" strings judged to be the same issue although quoted in different places
    (written by the orchestrator after reading all role files; see SKILL.md step 4)."""
    induk = list(range(len(temuan)))

    def akar(i):
        while induk[i] != i:
            induk[i] = induk[induk[i]]
            i = induk[i]
        return i

    def satukan(i, j):
        induk[akar(i)] = akar(j)

    for i in range(len(temuan)):
        for j in range(i):
            if mirip(temuan[i], temuan[j]):
                satukan(i, j)
    indeks = {t["uid"]: i for i, t in enumerate(temuan)}
    for grup in gabungan or []:
        ada = [indeks[u] for u in grup if u in indeks]
        for i in ada[1:]:
            satukan(i, ada[0])
    peta = {}
    for i, t in enumerate(temuan):
        peta.setdefault(akar(i), []).append(t)
    kelompok = list(peta.values())
    hasil = []
    for k in kelompok:
        utama = min(k, key=lambda t: (RANK[t["severity"]], -len(t["problem"])))
        peran = sorted({t["role"] for t in k})
        hasil.append({**utama, "roles": peran, "consensus": len(peran),
                      "severity": min((t["severity"] for t in k), key=RANK.get),
                      "members": [t["uid"] for t in k]})
    return sorted(hasil, key=lambda c: (RANK[c["severity"]], -c["consensus"], c["line"] or 0))


def putuskan(kl, skor, mesin_berat):
    kritis = [c for c in kl if c["severity"] == "critical"]
    mayor = [c for c in kl if c["severity"] == "major"]
    alasan = []
    med = {d: v["median"] for d, v in skor.items()}
    if any(c["consensus"] >= 2 for c in kritis):
        alasan.append("a critical issue raised independently by two or more roles")
    if med.get("originality", 5) <= 2 and med.get("significance", 5) <= 2:
        alasan.append("median originality and significance both at or below 2")
    if alasan:
        return "Reject in current form", alasan
    if kritis:
        alasan.append(f"{len(kritis)} critical issue(s) from a single role")
    if len(mayor) >= 3:
        alasan.append(f"{len(mayor)} major issues")
    if alasan:
        return "Major revision", alasan
    if mayor or mesin_berat:
        return "Minor revision", [f"{len(mayor)} major issue(s)", f"{mesin_berat} machine blocker(s)"]
    return "Accept with polishing", ["no critical or major issue"]


def tulis_laporan(ws, meta, kl, skor, tak_terverifikasi, mesin, galat, keputusan, alasan, da):
    L = []
    L.append(f"# Review report\n\nManuscript: `{meta.get('source', '')}`  ")
    L.append(f"SHA-256: `{meta.get('sha256', '')[:16]}…` · {meta.get('words', 0)} words · "
             f"roles: {', '.join(sorted({r for c in kl for r in c['roles']}))}\n")
    L.append(f"## Decision: {keputusan}\n")
    L += [f"- {a}" for a in alasan]
    L.append("\n## Scorecard (1–5, median across roles)\n")
    L.append("| Dimension | Median | Range | Note |\n|---|---|---|---|")
    for d in DIMENSIONS:
        if d in skor:
            v = skor[d]
            L.append(f"| {d} | {v['median']:.1f} | {v['min']}–{v['max']} | "
                     f"{'reviewers disagree' if v['max'] - v['min'] >= 2 else ''} |")
    berat = [m for m in mesin if m["weight"] == "heavy"]
    if berat:
        L.append("\n## Submission blockers (machine checks)\n")
        L += [f"- L{m['line']}: {m['message']}" for m in berat]
    konsensus = [c for c in kl if c["consensus"] >= 2]
    tunggal = [c for c in kl if c["consensus"] == 1]
    for judul, daftar in (("Issues raised by two or more roles", konsensus),
                          ("Issues raised by one role", tunggal)):
        if not daftar:
            continue
        L.append(f"\n## {judul}\n")
        for c in daftar:
            L.append(f"### [{c['severity'].upper()}] {c['title']}\n")
            L.append(f"L{c['line']} · {c['section']} · {c['dimension']} · roles: {', '.join(c['roles'])}"
                     f" · confidence: {c.get('confidence', 'n/a')}\n")
            L.append(f"> {normal(c['quote'])[:300]}\n")
            L.append(f"**Problem.** {c['problem']}\n\n**Fix.** {c['fix']}\n")
    if da:
        L.append("\n## Strongest counter-argument (devil's advocate)\n")
        L.append(da + "\n")
    L.append("\n## Revision roadmap\n")
    for i, c in enumerate([c for c in kl if c["severity"] != "minor"], 1):
        L.append(f"{i}. **{c['title']}** ({c['severity']}, L{c['line']}, {c['section']}) — {c['fix']}")
    kecil = [c for c in kl if c["severity"] == "minor"]
    if kecil:
        L.append(f"\nPlus {len(kecil)} minor issue(s) listed above.")
    if tak_terverifikasi:
        L.append("\n## Findings set aside: quote not found in the manuscript\n")
        L.append("These do not count toward the decision. Re-check or discard.\n")
        L += [f"- ({t['role']}) {t['title']} — quote: \"{normal(t['quote'])[:120]}\"" for t in tak_terverifikasi]
    if galat:
        L.append("\n## Schema errors\n")
        L += [f"- {g}" for g in galat]
    with open(os.path.join(ws, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ws = argv[0]
    baris, seksi, mesin = muat(ws)
    meta = {}
    if os.path.exists(os.path.join(ws, "meta.json")):
        with open(os.path.join(ws, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
    semua, galat, skor_mentah, da = [], [], {d: [] for d in DIMENSIONS}, ""
    peran_jalan = set()
    folder = os.path.join(ws, "findings")
    for nama in sorted(os.listdir(folder)):
        if not nama.endswith(".json"):
            continue
        role = nama[:-5]
        peran_jalan.add(role)
        try:
            with open(os.path.join(folder, nama), encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            galat.append(f"{role}: invalid JSON ({e})")
            continue
        g = validasi(role, data)
        galat += g
        if any(x.startswith(f"{role}: missing") or "top level" in x for x in g):
            continue
        for d, v in data["scores"].items():
            if d in skor_mentah and isinstance(v, (int, float)):
                skor_mentah[d].append(v)
        if data.get("strongest_counterargument"):
            da = data["strongest_counterargument"]
        for i, t in enumerate(data["findings"], 1):
            if t.get("severity") not in SEVERITIES or t.get("dimension") not in DIMENSIONS:
                continue
            t = {**t, "role": role, "id": t.get("id") or f"{role}-{i}"}
            t["uid"] = f"{role}:{t['id']}"
            t["quote_verified"], t["line"] = verifikasi(t, baris)
            t["section"] = seksi_untuk(t["line"], seksi)
            semua.append(t)
    terverifikasi = [t for t in semua if t["quote_verified"]]
    tak = [t for t in semua if not t["quote_verified"]]
    gabungan = []
    berkas_gabung = os.path.join(ws, "merges.json")
    if os.path.exists(berkas_gabung):
        with open(berkas_gabung, encoding="utf-8") as f:
            gabungan = json.load(f)
        dikenal = {t["uid"] for t in semua}
        galat += [f"merges.json: unknown finding '{u}'" for g in gabungan for u in g if u not in dikenal]
    kl = klaster(terverifikasi, gabungan)
    skor = {d: {"median": statistics.median(v), "min": min(v), "max": max(v)}
            for d, v in skor_mentah.items() if v}
    mesin_berat = sum(1 for m in mesin if m["weight"] == "heavy")
    keputusan, alasan = putuskan(kl, skor, mesin_berat)
    tulis_laporan(ws, meta, kl, skor, tak, mesin, galat, keputusan, alasan, da)
    with open(os.path.join(ws, "findings_final.json"), "w", encoding="utf-8") as f:
        json.dump({"decision": keputusan, "scores": skor, "clusters": kl, "set_aside": tak,
                   "roles_run": sorted(peran_jalan)},
                  f, ensure_ascii=False, indent=1)
    print(f"{keputusan}: {len(kl)} issue clusters ({sum(c['consensus'] >= 2 for c in kl)} with consensus), "
          f"{len(tak)} set aside (quote not found), {len(galat)} schema error(s)\n"
          f"report: {os.path.join(ws, 'report.md')}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
