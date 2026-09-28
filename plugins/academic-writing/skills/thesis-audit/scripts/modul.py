"""Shared definitions for thesis-audit: the module registry, levels, and section kinds.

Modules are ordered along the research chain. Order matters: the action plan fixes upstream
modules first, because a change there (the problem statement, the method) moves everything
downstream of it.
"""

import re

LEVELS = ["skripsi", "tesis", "disertasi"]

# (id, English name, Indonesian name, levels it applies to)
MODULES = [
    ("M01", "Structure and completeness", "Struktur dan kelengkapan", LEVELS),
    ("M02", "Problem - objective - conclusion chain", "Rantai masalah - tujuan - kesimpulan", LEVELS),
    ("M03", "Background and gap evidence", "Latar belakang dan bukti celah", LEVELS),
    ("M04", "Literature and theory", "Tinjauan pustaka dan landasan teori", LEVELS),
    ("M05", "Method fits the questions", "Kesesuaian metode dengan pertanyaan", LEVELS),
    ("M06", "Constructs, variables, requirements", "Konstruk, variabel, kebutuhan sistem", LEVELS),
    ("M07", "Data, sample, and numbers", "Data, sampel, dan angka", LEVELS),
    ("M08", "Analysis, testing, and interpretation", "Analisis, pengujian, dan penafsiran", LEVELS),
    ("M09", "Claims sized to evidence", "Klaim sebanding dengan bukti", LEVELS),
    ("M10", "Consistency across chapters", "Konsistensi antarbab", LEVELS),
    ("M11", "Citations and references", "Sitasi dan daftar pustaka", LEVELS),
    ("M12", "Integrity risks", "Risiko integritas", LEVELS),
    ("M13", "Contribution and originality", "Kontribusi dan kebaruan", LEVELS),
    ("M14", "Dissertation thread and publications", "Benang merah disertasi dan publikasi", ["disertasi"]),
]
URUT = {m[0]: i for i, m in enumerate(MODULES)}

STATUS = ["found", "not_found", "not_assessable", "not_applicable"]
COVERAGE = ["full", "partial", "limited"]
SEVERITY = ["critical", "major", "minor"]
RANK = {s: i for i, s in enumerate(SEVERITY)}
FSTATUS = ["confirmed", "likely", "potential"]
CONFIDENCE = ["high", "medium", "low"]

# Section kinds, most specific first: "Tujuan Penelitian" must not be read as a chapter title.
JENIS = [
    ("rumusan", r"rumusan masalah|^(?:the )?problem$|research problem|research questions?|problem statement|pertanyaan penelitian|identifikasi masalah"),
    ("tujuan", r"tujuan penelitian|^tujuan\b|objectives?|research aims?"),
    ("hipotesis", r"hipotesis|hypothes[ie]s"),
    ("batasan", r"batasan masalah|ruang lingkup|scope|delimitation"),
    ("manfaat", r"manfaat penelitian|significance of the study|contribution"),
    ("kesimpulan", r"kesimpulan|simpulan|conclusions?"),
    ("saran", r"^saran|future work|recommendations?"),
    ("rujukan", r"daftar pustaka|referensi|references|bibliography"),
    ("abstrak", r"abstrak|abstract|intisari"),
    ("pendahuluan", r"pendahuluan|introduction|\bbab i\b(?!i|v)"),
    ("pustaka", r"tinjauan pustaka|landasan teori|kajian pustaka|kajian teori|penelitian terdahulu|penelitian terkait|"
                r"literature review|related work|\bbab ii\b(?!i)"),
    ("metode", r"metodologi|metode penelitian|research method|methodology|methods|\bbab iii\b"),
    ("hasil", r"hasil|pembahasan|results|discussion|implementasi|\bbab iv\b"),
    ("penutup", r"penutup|\bbab v\b"),
]

# Parts every level is expected to have
WAJIB = ["abstrak", "pendahuluan", "rumusan", "tujuan", "pustaka", "metode", "hasil", "kesimpulan", "rujukan"]


def jenis_judul(judul):
    t = re.sub(r"^[\d.\s]+", "", judul.strip().lower())
    for k, pola in JENIS:
        if re.search(pola, t):
            return k
    return ""


def nama_modul(mid, bahasa):
    for m in MODULES:
        if m[0] == mid:
            return m[2] if bahasa == "id" else m[1]
    return mid


def modul_untuk(level):
    return [m[0] for m in MODULES if level in m[3]]
