"""Compare two consolidated reviews of the same manuscript (before and after revision).

Each argument is a workspace consolidated by consolidate_review.py. Issues from the earlier
review are matched to the later one by quote overlap or by title/problem wording; line numbers
are not used, because revision moves lines.

    python diff_review.py review/2026-09-28 review/2026-10-15

Writes <new>/diff.md and prints a summary: resolved, still open, not re-checked, new, and score
changes. Issues whose raising roles did not run in the later review are reported as not
re-checked, never as resolved. Exit status 1 if any earlier critical or major issue is still
open or not re-checked.
"""

import json
import os
import re
import sys


def muat(ws):
    with open(os.path.join(ws, "findings_final.json"), encoding="utf-8") as f:
        return json.load(f)


def normal(t):
    return re.sub(r"\s+", " ", t.replace("**", "").replace("`", "")).strip().lower()


def kata(t):
    return {w for w in re.findall(r"[a-z]{4,}", t.lower())}


def sama(a, b):
    qa, qb = normal(a.get("quote", "")), normal(b.get("quote", ""))
    if len(qa) >= 12 and len(qb) >= 12 and (qa in qb or qb in qa):
        return True
    ka = kata(a["title"] + " " + a.get("problem", ""))
    kb = kata(b["title"] + " " + b.get("problem", ""))
    return a.get("dimension") == b.get("dimension") and bool(ka and kb) and len(ka & kb) / len(ka | kb) >= 0.35


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    lama, baru = muat(argv[0]), muat(argv[1])
    sisa_baru = list(baru["clusters"])
    dijalankan = set(baru.get("roles_run") or {r for c in baru["clusters"] for r in c["roles"]})
    selesai, terbuka, belum = [], [], []
    for a in lama["clusters"]:
        pasangan = next((b for b in sisa_baru if sama(a, b)), None)
        if pasangan:
            terbuka.append((a, pasangan))
            sisa_baru.remove(pasangan)
        elif set(a["roles"]) & dijalankan:
            selesai.append(a)
        else:
            belum.append(a)  # no role that raised it ran again, so it cannot count as resolved

    L = [f"# Re-review: {argv[0]} -> {argv[1]}", "",
         f"Decision: **{lama['decision']}** -> **{baru['decision']}**", "",
         "## Scores", "", "| Dimension | Before | After | Change |", "|---|---|---|---|"]
    for d in sorted(set(lama["scores"]) | set(baru["scores"])):
        s0 = lama["scores"].get(d, {}).get("median")
        s1 = baru["scores"].get(d, {}).get("median")
        ubah = f"{s1 - s0:+.1f}" if s0 is not None and s1 is not None else ""
        L.append(f"| {d} | {s0 if s0 is not None else '-'} | {s1 if s1 is not None else '-'} | {ubah} |")
    L += ["", f"## Resolved ({len(selesai)})", ""]
    L += [f"- [{a['severity']}] {a['title']}" for a in selesai]
    L += ["", f"## Still open ({len(terbuka)})", ""]
    L += [f"- [{a['severity']} -> {b['severity']}] {b['title']} (now L{b['line']})" for a, b in terbuka]
    L += ["", f"## Not re-checked ({len(belum)}): the roles that raised these did not run again", ""]
    L += [f"- [{a['severity']}] {a['title']} (roles: {', '.join(a['roles'])})" for a in belum]
    L += ["", f"## New ({len(sisa_baru)})", ""]
    L += [f"- [{b['severity']}] {b['title']} (L{b['line']})" for b in sisa_baru]
    with open(os.path.join(argv[1], "diff.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    serius = ([a for a, _ in terbuka if a["severity"] in ("critical", "major")]
              + [a for a in belum if a["severity"] in ("critical", "major")])
    print(f"{lama['decision']} -> {baru['decision']}: {len(selesai)} resolved, {len(terbuka)} still open, "
          f"{len(belum)} not re-checked, {len(sisa_baru)} new; {len(serius)} critical/major unresolved\n"
          f"report: {os.path.join(argv[1], 'diff.md')}")
    return 1 if serius else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
