"""Check an audit.json against its workspace and write the reports.

The audit is written by a model; this script is what keeps it honest. It rejects, rather than
trusts, the model's own bookkeeping:

  - every module for the level appears exactly once, with a valid status and coverage;
  - status agrees with the findings: `found` needs at least one verified finding owned by the
    module, every other status needs none; `not_assessable` must name the missing input;
  - every quote is found in the manuscript (the line is corrected); findings whose quote is not
    there are set aside and count for nothing;
  - severity is capped by evidence: `critical` needs status `confirmed` and confidence `high`;
    `major` needs `confirmed` or `likely`; a `potential` issue can only be `minor`;
  - finding IDs are unique, related modules exist, defence questions point at real findings;
  - totals are computed here, never copied from the audit.

Writes:
  report.md     for the supervisor or the author: verdict, module matrix, findings, action plan
  feedback.md   for the student (skripsi/tesis): the top items per chapter, plain actions,
                practice questions for the defence — no internal statuses or confidence
  audit_final.json

Usage:
    python report_audit.py audit/budi/2026-10-01 [--top 12]
Exit status: 0 reports written, 1 audit inconsistent (reports still written, errors listed), 2 usage.
"""

import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "manuscript-review", "scripts"))
from modul import (CONFIDENCE, COVERAGE, FSTATUS, RANK, SEVERITY, STATUS, URUT,  # noqa: E402
                   modul_untuk, nama_modul)
from consolidate_review import normal, verifikasi  # noqa: E402

T = {
    "id": {"report": "Laporan audit", "verdict": "Kesimpulan", "summary": "Ringkasan", "matrix": "Status modul",
           "module": "Modul", "status": "Status", "coverage": "Cakupan", "findings": "Temuan",
           "totals": "Jumlah", "machine": "Pemeriksaan mesin (perbaiki dulu, bersifat mekanis)",
           "plan": "Rencana perbaikan", "na": "Tidak dapat dinilai", "defence": "Pertanyaan sidang",
           "aside": "Temuan disisihkan: kutipan tidak ditemukan di naskah", "errors": "Audit tidak konsisten",
           "problem": "Masalah", "fix": "Perbaikan", "why": "Mengapa ditanyakan", "answer": "Jawaban yang kuat",
           "feedback": "Umpan balik bimbingan", "todo": "Yang perlu Anda lakukan",
           "practice": "Latihan pertanyaan sidang", "more": "butir lain menyusul sesudah butir di atas selesai",
           "found": "ditemukan", "not_found": "tidak ditemukan", "not_assessable": "tidak dapat dinilai",
           "not_applicable": "tidak berlaku", "missing": "yang kurang",
           "verdicts": ["Belum layak diuji", "Revisi mayor", "Revisi minor", "Siap diuji"]},
    "en": {"report": "Audit report", "verdict": "Verdict", "summary": "Summary", "matrix": "Module status",
           "module": "Module", "status": "Status", "coverage": "Coverage", "findings": "Findings",
           "totals": "Totals", "machine": "Machine checks (mechanical; fix first)",
           "plan": "Action plan", "na": "Not assessable", "defence": "Defence questions",
           "aside": "Findings set aside: quote not found in the manuscript", "errors": "Audit inconsistent",
           "problem": "Problem", "fix": "Fix", "why": "Why it will be asked", "answer": "A strong answer",
           "feedback": "Supervision feedback", "todo": "What to do",
           "practice": "Defence practice questions", "more": "more items follow once these are done",
           "found": "found", "not_found": "not found", "not_assessable": "not assessable",
           "not_applicable": "not applicable", "missing": "missing",
           "verdicts": ["Not ready for examination", "Major revision", "Minor revision", "Ready for examination"]},
}


def muat(ws, nama, bawaan=None):
    p = os.path.join(ws, nama)
    if not os.path.exists(p):
        return bawaan
    with open(p, encoding="utf-8") as f:
        return json.load(f) if nama.endswith(".json") else f.read()


def seksi_untuk(no, seksi, bab=False):
    if bab:  # a chapter runs until the next top-level heading, past its own subsections
        kandidat = [s for s in seksi if s["level"] == min(x["level"] for x in seksi) and s["start"] <= (no or 0)]
    else:
        kandidat = [s for s in seksi if s["start"] <= (no or 0) <= s["end"]]
    return kandidat[-1]["title"] if kandidat else ""


def periksa(audit, meta, baris, seksi):
    galat, temuan, sisih = [], [], []
    wajib = modul_untuk(meta["level"])
    mod = audit.get("modules") or {}
    for mid in wajib:
        m = mod.get(mid)
        if not isinstance(m, dict):
            galat.append(f"{mid}: module missing")
            continue
        if m.get("status") not in STATUS:
            galat.append(f"{mid}: status must be one of {STATUS}")
        if m.get("status") in ("found", "not_found") and m.get("coverage") not in COVERAGE:
            galat.append(f"{mid}: coverage must be one of {COVERAGE}")
        if m.get("status") == "not_assessable" and not m.get("missing"):
            galat.append(f"{mid}: not_assessable must say what input is missing")
        if not m.get("basis"):
            galat.append(f"{mid}: 'basis' (what was checked, or why it does not apply) is empty")
    galat += [f"{mid}: not a module for level {meta['level']}" for mid in mod if mid not in wajib]

    ids = set()
    for i, t in enumerate(audit.get("findings") or [], 1):
        tag = t.get("id") or f"#{i}"
        if tag in ids:
            galat.append(f"{tag}: duplicate finding id")
        ids.add(tag)
        for k in ("id", "module", "title", "severity", "status", "confidence", "quote", "problem", "fix"):
            if not t.get(k):
                galat.append(f"{tag}: missing '{k}'")
        if t.get("module") not in wajib:
            galat.append(f"{tag}: unknown module '{t.get('module')}'")
        for k, sah in (("severity", SEVERITY), ("status", FSTATUS), ("confidence", CONFIDENCE)):
            if t.get(k) and t[k] not in sah:
                galat.append(f"{tag}: {k} must be one of {sah}")
        if t.get("severity") == "critical" and (t.get("status") != "confirmed" or t.get("confidence") != "high"):
            galat.append(f"{tag}: critical needs status 'confirmed' and confidence 'high'; "
                         "lower the severity or show stronger evidence")
        if t.get("severity") == "major" and t.get("status") == "potential":
            galat.append(f"{tag}: a potential issue can only be minor")
        galat += [f"{tag}: related module '{r}' does not exist" for r in t.get("related") or [] if r not in wajib]
        if t.get("module") not in wajib or t.get("severity") not in SEVERITY:
            continue
        t = dict(t)
        ok, t["line"] = verifikasi(t, baris)
        t["section"] = seksi_untuk(t["line"], seksi)
        t["chapter"] = seksi_untuk(t["line"], seksi, bab=True) or t["section"]
        (temuan if ok else sisih).append(t)

    milik = {mid: [t for t in temuan if t["module"] == mid] for mid in wajib}
    for mid in wajib:
        st = (mod.get(mid) or {}).get("status")
        n = len(milik[mid])
        if st == "found" and not n:
            galat.append(f"{mid}: status 'found' but no verified finding belongs to it")
        if st in ("not_found", "not_assessable", "not_applicable") and n:
            galat.append(f"{mid}: status '{st}' but {n} verified finding(s) belong to it")
    for q in audit.get("defence_questions") or []:
        for fid in q.get("findings") or []:
            if fid not in ids:
                galat.append(f"defence question '{q.get('question', '')[:40]}…': unknown finding '{fid}'")
    return galat, temuan, sisih, milik


def putuskan(temuan, mesin_berat):
    n = {s: sum(1 for t in temuan if t["severity"] == s) for s in SEVERITY}
    if n["critical"]:
        return 0
    if n["major"] >= 3:
        return 1
    if n["major"] or mesin_berat:
        return 2
    return 3


def urut_rencana(temuan):
    # severity first; within it, upstream modules first, because fixing them moves what follows
    return sorted(temuan, key=lambda t: (RANK[t["severity"]], URUT[t["module"]], t["line"] or 0))


def tulis_laporan(ws, meta, audit, temuan, sisih, milik, mesin, galat, keputusan, L_):
    b = meta["lang"]
    L = [f"# {L_['report']}: {meta['level']}", "",
         f"`{meta['source']}` · SHA-256 `{meta['sha256'][:16]}…` · {meta['words']} words · "
         f"{audit.get('research_type', '?')}", "",
         f"## {L_['verdict']}: {L_['verdicts'][keputusan]}", ""]
    if audit.get("summary"):
        L += [f"**{L_['summary']}.** {audit['summary']}", ""]
    n = {s: sum(1 for t in temuan if t["severity"] == s) for s in SEVERITY}
    L += [f"{L_['totals']}: critical {n['critical']} · major {n['major']} · minor {n['minor']} = {len(temuan)}"
          f" · machine heavy {sum(1 for m in mesin if m['weight'] == 'heavy')}", "",
          f"## {L_['matrix']}", "", f"| ID | {L_['module']} | {L_['status']} | {L_['coverage']} | {L_['findings']} |",
          "|---|---|---|---|---|"]
    for mid, daftar in milik.items():
        m = (audit.get("modules") or {}).get(mid) or {}
        L.append(f"| {mid} | {nama_modul(mid, b)} | {L_.get(m.get('status'), '?')} | {m.get('coverage', '')} | {len(daftar)} |")
    berat = [m for m in mesin if m["weight"] == "heavy"]
    if berat:
        L += ["", f"## {L_['machine']}", ""] + [f"- L{m['line']}: {m['message']}" for m in berat]
    for s in SEVERITY:
        daftar = [t for t in temuan if t["severity"] == s]
        if not daftar:
            continue
        L += ["", f"## {s.upper()} ({len(daftar)})", ""]
        for t in sorted(daftar, key=lambda t: t["line"] or 0):
            L += [f"### {t['id']} · {t['title']}", "",
                  f"L{t['line']} · {t['section']} · {t['module']} {nama_modul(t['module'], b)} · "
                  f"{t['status']} · confidence {t['confidence']}"
                  + (f" · related {', '.join(t['related'])}" if t.get("related") else ""), "",
                  f"> {normal(t['quote'])[:300]}", "",
                  f"**{L_['problem']}.** {t['problem']}", "", f"**{L_['fix']}.** {t['fix']}", ""]
    na = [(mid, m) for mid, m in (audit.get("modules") or {}).items() if m.get("status") == "not_assessable"]
    if na:
        L += [f"## {L_['na']}", ""] + [f"- {mid} {nama_modul(mid, b)} — {L_['missing']}: {m.get('missing')}" for mid, m in na]
    L += ["", f"## {L_['plan']}", ""]
    i = 0
    if berat:
        i += 1
        L.append(f"{i}. {L_['machine']} ({len(berat)})")
    for t in urut_rencana([t for t in temuan if t["severity"] != "minor"]):
        i += 1
        L.append(f"{i}. **{t['title']}** ({t['severity']}, {t['module']}, L{t['line']}) — {t['fix']}")
    if n["minor"]:
        L.append(f"\n+ {n['minor']} minor.")
    dq = audit.get("defence_questions") or []
    if dq:
        L += ["", f"## {L_['defence']}", ""]
        for q in dq:
            L += [f"- **{q.get('question')}** ({', '.join(q.get('findings') or [])})",
                  f"  {L_['why']}: {q.get('why', '')}", f"  {L_['answer']}: {q.get('strong_answer', '')}"]
    if sisih:
        L += ["", f"## {L_['aside']}", ""] + [f"- {t['id']} {t['title']} — \"{normal(t['quote'])[:120]}\"" for t in sisih]
    if galat:
        L += ["", f"## {L_['errors']}", ""] + [f"- {g}" for g in galat]
    with open(os.path.join(ws, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def tulis_umpan_balik(ws, meta, audit, temuan, mesin, keputusan, L_, top):
    utama = urut_rencana(temuan)[:top]
    sisa_minor = sum(1 for t in temuan if t not in utama)
    L = [f"# {L_['feedback']}", "", f"**{L_['verdict']}: {L_['verdicts'][keputusan]}**", ""]
    berat = [m for m in mesin if m["weight"] == "heavy"]
    if berat:
        L += [f"## {L_['machine']}", ""] + [f"- L{m['line']}: {m['message']}" for m in berat] + [""]
    urutan_bab = []
    for t in sorted(utama, key=lambda t: t["line"] or 0):
        if t["chapter"] not in urutan_bab:
            urutan_bab.append(t["chapter"])
    no = 0
    for bab in urutan_bab:
        L += [f"## {bab or '-'}", ""]
        for t in sorted([t for t in utama if t["chapter"] == bab], key=lambda t: t["line"] or 0):
            no += 1
            L += [f"{no}. **{t['title']}** (L{t['line']}, {t['section']})", f"   > {normal(t['quote'])[:200]}",
                  f"   {t['problem']}", f"   **{L_['todo']}:** {t['fix']}", ""]
    if sisa_minor:
        L += [f"_{sisa_minor} {L_['more']}._", ""]
    dq = audit.get("defence_questions") or []
    if dq:
        L += [f"## {L_['practice']}", ""] + [f"- {q.get('question')}" for q in dq]
    with open(os.path.join(ws, "feedback.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    top = 12
    if "--top" in argv:
        i = argv.index("--top")
        top = int(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 1:
        print(__doc__)
        return 2
    ws = argv[0]
    meta = muat(ws, "meta.json")
    audit = muat(ws, "audit.json")
    if not meta or audit is None:
        print(f"{ws}: needs meta.json (prepare_audit.py) and audit.json (the audit)")
        return 2
    baris = muat(ws, "manuscript.md").splitlines()
    seksi, mesin = muat(ws, "sections.json", []), muat(ws, "machine.json", [])
    L_ = T.get(meta["lang"], T["en"])
    galat, temuan, sisih, milik = periksa(audit, meta, baris, seksi)
    keputusan = putuskan(temuan, sum(1 for m in mesin if m["weight"] == "heavy"))
    tulis_laporan(ws, meta, audit, temuan, sisih, milik, mesin, galat, keputusan, L_)
    if meta["level"] != "disertasi":
        tulis_umpan_balik(ws, meta, audit, temuan, mesin, keputusan, L_, top)
    with open(os.path.join(ws, "audit_final.json"), "w", encoding="utf-8") as f:
        json.dump({"verdict": L_["verdicts"][keputusan], "findings": temuan, "set_aside": sisih,
                   "errors": galat, "modules": {k: len(v) for k, v in milik.items()}},
                  f, ensure_ascii=False, indent=1)
    print(f"{L_['verdicts'][keputusan]}: {len(temuan)} verified finding(s), {len(sisih)} set aside, "
          f"{len(galat)} inconsistenc{'y' if len(galat) == 1 else 'ies'}\nreport: {os.path.join(ws, 'report.md')}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
