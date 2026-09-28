"""Grammar and spelling check of a Markdown manuscript with LanguageTool (optional).

Catches what check_manuscript_en.py cannot: articles, agreement, prepositions, confused words,
spelling. Runs LanguageTool locally (Java 17+ required; the first run downloads ~260 MB).

    pip install language_tool_python
    python check_grammar_lt.py manuscript.md               # British English
    python check_grammar_lt.py --lang en-US manuscript.md
    python check_grammar_lt.py --allow words.txt manuscript.md   # one allowed word per line

Blockquotes, tables, code, and figure captions are skipped. Spelling hits on capitalised words
(author names, acronyms) are dropped unless --all is given, because in a research paper nearly
all of them are proper nouns. Exit status 1 if any GRAMMAR, CONFUSED_WORDS, or COLLOCATIONS
match remains.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_manuscript_en as cm  # noqa: E402

BERAT = {"GRAMMAR", "CONFUSED_WORDS", "COLLOCATIONS"}


def main(argv):
    lang, allow, semua, paths = "en-GB", set(), False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--lang":
            lang = argv[i + 1]; i += 2; continue
        if a == "--allow":
            with open(argv[i + 1], encoding="utf-8") as f:
                allow = {w.strip() for w in f if w.strip()}
            i += 2; continue
        if a == "--all":
            semua = True; i += 1; continue
        paths.append(a); i += 1
    if not paths:
        print(__doc__)
        return 2
    try:
        import language_tool_python
    except ImportError:
        print("language_tool_python is not installed: pip install language_tool_python")
        return 2
    tool = language_tool_python.LanguageTool(lang)
    berat_total = 0
    for p in paths:
        abstrak, badan, _, _ = cm.bagian(cm.baca(p))
        for no, par in abstrak + badan:
            if par.lstrip().startswith(("|", "```")) or cm.KETERANGAN.match(par.strip()):
                continue
            teks = re.sub(r"`[^`]*`", "X", par).replace("**", "").replace("*", "")
            for m in tool.check(teks):
                kata = teks[m.offset:m.offset + m.error_length]
                if m.category == "BRE_STYLE_OXFORD_SPELLING":
                    continue
                if m.rule_id.startswith("MORFOLOGIK") and not semua and (kata[:1].isupper() or kata in allow):
                    continue
                if m.category in BERAT:
                    berat_total += 1
                konteks = teks[max(0, m.offset - 35):m.offset + m.error_length + 35]
                saran = ", ".join(m.replacements[:3])
                print(f"L{no} [{m.category}/{m.rule_id}] {m.message[:80]}\n    ...{konteks}...  -> {saran}")
    tool.close()
    print(f"\n{berat_total} grammar/confusion/collocation matches")
    return 1 if berat_total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
