"""Pemeriksa gaya bahasa untuk modul, naskah buku ajar, dan dokumen ajar lain.

Menandai pola yang membuat prosa terbaca sebagai tulisan mesin: pengantar yang
tidak membawa isi, kata besar tanpa keterangan, penutup yang mengulang isi,
pertanyaan retoris berjawab sendiri, dan paragraf yang seluruhnya butir.

Pemeriksa ini tidak menebak siapa yang menulis. Ia hanya menunjukkan polanya,
beserta baris dan kolomnya, supaya penulis bisa menilai sendiri. Satu temuan
tidak otomatis berarti kalimatnya buruk — `Bayangkan Anda diminta menghitung
rata-rata 40 nilai` adalah alat peraga yang sah, sedangkan `Bayangkan jika
semua data hilang` adalah retorika kosong. Karena itu keluarannya daftar
periksa, bukan nilai.

Aturannya ada di `pola/claudish_id.json`, bukan di berkas ini. Menambah pola
cukup menyunting JSON-nya.

Blok kode, kode sebaris, alamat tautan, dan komentar HTML dibuang lebih dahulu,
jadi `robust` di dalam `def robust():` tidak ikut tertandai.

Pemakaian:
    python periksa_gaya.py --semua
    python periksa_gaya.py --semua --berat
    python periksa_gaya.py naskah/Bab_02_Algoritma.md
    python periksa_gaya.py --semua --ringkas

Pilihan:
    --semua     periksa seluruh berkas .md di bawah folder kerja
    --berat     hanya tampilkan temuan berbobot berat
    --ringkas   satu baris per temuan, tanpa saran perbaikan
    --pola X    pakai berkas aturan lain

Keluar dengan status 1 bila ada temuan berbobot berat.
"""

import json
import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent
AKAR_REPO = Path.cwd()   # --semua memeriksa folder kerja saat ini
POLA_BAKU = AKAR / "pola" / "claudish_id.json"

# Berkas yang diperiksa oleh --semua: seluruh .md di bawah folder kerja.
SASARAN = [
    "**/*.md",
]

ABAIKAN_BERKAS = "gaya:abaikan-berkas"
ABAIKAN_BARIS = "gaya:abaikan"

PISAH = "—"          # tanda pisah em
SEPI = re.compile(r"^\s*\|?\s*[-:| ]+\s*\|?\s*$")


class Temuan:
    """Satu pola yang ditemukan, lengkap dengan letaknya."""

    def __init__(self, berkas, baris, kolom, kode, bobot, pesan, saran, kutipan):
        self.berkas = berkas
        self.baris = baris
        self.kolom = kolom
        self.kode = kode
        self.bobot = bobot
        self.pesan = pesan
        self.saran = saran
        self.kutipan = kutipan


def muat_pola(berkas):
    with open(berkas, encoding="utf-8") as f:
        pola = json.load(f)
    for aturan in pola["leksikal"]:
        aturan["terkompilasi"] = [
            re.compile(p, re.IGNORECASE) for p in aturan["pola"]]
    return pola


def bersihkan(teks):
    """Buang bagian yang bukan prosa, panjang baris tetap supaya kolom cocok."""

    def kosongkan(m):
        return " " * (m.end() - m.start())

    teks = re.sub(r"`[^`]*`", kosongkan, teks)              # kode sebaris
    teks = re.sub(r"\]\([^)]*\)", kosongkan, teks)          # alamat tautan
    teks = re.sub(r"<!--.*?-->", kosongkan, teks)           # komentar HTML
    teks = re.sub(r"https?://\S+", kosongkan, teks)         # tautan telanjang
    return teks


# Pagar blok kode: tiga tanda atau lebih, lalu paling banyak satu kata
# keterangan bahasa (`python`, `text`, `c++`) dan tidak ada apa-apa lagi.
#
# Syarat itu bukan kerewelan. Penanda caret pada traceback Python 3.12
# berbentuk `~~~~~~^~~~~~~~` atau `~~~~^^^^^^^^^`, dan pola yang hanya menuntut
# tiga tanda di awal baris akan menganggapnya pembuka blok. Hitungan buka-tutup
# lalu bergeser, dan seluruh sisa berkas berhenti diperiksa tanpa satu pun
# keluhan — kegagalan yang paling berbahaya bagi sebuah pemeriksa, karena ia
# terbaca sebagai lulus. Versi sebelumnya hanya melarang tanda pagar di
# belakangnya, dan bentuk kedua di atas — tilde lalu caret saja — lolos.
PAGAR = re.compile(r"^\s*(`{3,}|~{3,})\s*[\w+#.-]*\s*$")


def baca(berkas):
    """Kembalikan daftar (nomor, teks bersih, jenis) untuk baris yang diperiksa.

    Jenis: judul, butir, tabel, atau prosa. Baris di dalam blok kode dan baris
    yang didahului penanda abaikan tidak dikembalikan sama sekali.
    """
    isi = Path(berkas).read_text(encoding="utf-8").splitlines()
    if any(ABAIKAN_BERKAS in b for b in isi[:10]):
        return []

    hasil = []
    dalam_kode = False
    lewati_berikutnya = False

    for nomor, mentah in enumerate(isi, start=1):
        if PAGAR.match(mentah):
            dalam_kode = not dalam_kode
            continue
        if dalam_kode:
            continue
        if ABAIKAN_BARIS in mentah and ABAIKAN_BERKAS not in mentah:
            lewati_berikutnya = True
            continue
        if lewati_berikutnya:
            lewati_berikutnya = False
            continue

        teks = bersihkan(mentah)
        if not teks.strip():
            hasil.append((nomor, "", "kosong"))
            continue
        if SEPI.match(teks):
            continue

        if re.match(r"^\s*#{1,6}\s", teks):
            jenis = "judul"
        elif re.match(r"^\s*([-*+]|\d+\.)\s", teks):
            jenis = "butir"
        elif teks.lstrip().startswith("|"):
            jenis = "tabel"
        else:
            jenis = "prosa"
        hasil.append((nomor, teks, jenis))

    return hasil


def paragraf(baris):
    """Kelompokkan baris prosa yang berurutan menjadi paragraf."""
    kumpulan = []
    sekarang = []
    for nomor, teks, jenis in baris:
        if jenis == "prosa":
            sekarang.append((nomor, teks))
        elif sekarang:
            kumpulan.append(sekarang)
            sekarang = []
    if sekarang:
        kumpulan.append(sekarang)
    return kumpulan


def periksa_leksikal(berkas, baris, pola):
    temuan = []
    for aturan in pola["leksikal"]:
        for nomor, teks, jenis in baris:
            if jenis in ("kosong",):
                continue
            for rx in aturan["terkompilasi"]:
                for m in rx.finditer(teks):
                    temuan.append(Temuan(
                        berkas, nomor, m.start() + 1, aturan["id"],
                        aturan["bobot"], aturan["pesan"], aturan["saran"],
                        m.group(0).strip()))
    return temuan


def _kata(teks):
    return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’-]*", teks)


# Rentang emoji sesungguhnya. Sengaja tidak memakai "semua di atas U+2500":
# penanda tingkat kesulitan ◆ (U+25C6), panah, centang, dan huruf Yunani pada
# notasi Big-O semuanya jatuh di sana dan bukan hiasan.
RENTANG_EMOJI = (
    (0x1F300, 0x1FAFF),   # piktograf, emotikon, simbol tambahan
    (0x1F000, 0x1F0FF),   # kartu dan ubin
    (0x2600, 0x26FF),     # simbol lain-lain: ☀ ☂ ⚡
    (0x2728, 0x27BF),     # dingbats bergaya emoji, ✓ dan ✗ tetap di luar
)


def _ada_emoji(teks):
    return any(any(a <= ord(c) <= b for a, b in RENTANG_EMOJI) or
               ord(c) == 0xFE0F
               for c in teks)


def periksa_struktur(berkas, baris, pola):
    ambang = pola["struktur"]
    temuan = []

    def catat(nomor, kode, bobot, pesan, saran, kutipan):
        temuan.append(Temuan(berkas, nomor, 1, kode, bobot, pesan, saran,
                             kutipan))

    prosa = [(n, t) for n, t, j in baris if j in ("prosa", "butir")]
    jumlah_kata = sum(len(_kata(t)) for _, t in prosa)

    # 1. Kepadatan tanda pisah.
    pisah = [(n, t) for n, t in prosa if PISAH in t]
    jumlah_pisah = sum(t.count(PISAH) for _, t in prosa)
    if jumlah_kata >= 400:
        per_seribu = jumlah_pisah * 1000.0 / jumlah_kata
        if per_seribu > ambang["pisah_per_1000_kata"]:
            catat(pisah[0][0] if pisah else 1, "pisah-berlebih", "ringan",
                  "Tanda pisah dipakai %.0f kali per 1.000 kata (ambang %d)."
                  % (per_seribu, ambang["pisah_per_1000_kata"]),
                  "Sebagian ganti dengan titik, koma, atau tanda kurung.",
                  "%d tanda pisah" % jumlah_pisah)

    # 1b. Kata penegas yang dipakai terlalu sering. Kata-kata ini sah satu-dua
    # kali; yang menandai tulisan mesin adalah kekerapannya, bukan
    # keberadaannya. Karena itu diperiksa sebagai kepadatan, bukan sebagai pola.
    kepadatan = ambang.get("kepadatan_kata", {})
    if jumlah_kata >= ambang.get("kepadatan_kata_minimum", 800):
        for kata, maks in kepadatan.items():
            rx = re.compile(r"\b%s\b" % re.escape(kata), re.IGNORECASE)
            tempat = [(n, t) for n, t in prosa if rx.search(t)]
            jumlah = sum(len(rx.findall(t)) for _, t in prosa)
            per_seribu = jumlah * 1000.0 / jumlah_kata
            if per_seribu > maks:
                catat(tempat[0][0] if tempat else 1, "penegas-berulang",
                      "berat",
                      "\"%s\" dipakai %d kali, %.1f per 1.000 kata "
                      "(ambang %d)." % (kata, jumlah, per_seribu, maks),
                      "Buang sebagian. Kata ini menandai tulisan mesin lewat "
                      "kekerapannya, bukan lewat keberadaannya.",
                      "%d kemunculan" % jumlah)

    # 1c. Rujukan sub-bab lintas bab yang tidak menyebut babnya. "§1.5" dibaca
    # dari dalam Bab 2 tidak memberi tahu pembaca bahwa ia harus membuka bab
    # lain. Hanya berlaku pada berkas naskah buku, yang namanya memuat nomor
    # babnya sendiri.
    m_bab = re.search(r"(?:Bab|Chapter|Ch)[_ -]?(?:[A-Za-z]+\d*[_-])?(\d+)", str(berkas))
    if m_bab:
        bab_ini = int(m_bab.group(1))
        ekor = ""      # ujung baris sebelumnya: "Bab 2" bisa terpisah baris
        for nomor, teks, jenis in baris:
            if jenis == "kosong":
                ekor = ""
                continue
            for m in re.finditer(r"§\s?(\d+)\.\d+", teks):
                if int(m.group(1)) == bab_ini:
                    continue
                awalan = (ekor + " " + teks[:m.start()])[-14:]
                if re.search(r"[Bb]ab\s*%s\s*$" % m.group(1), awalan):
                    continue
                catat(nomor, "rujukan-lintas-bab", "berat",
                      "Rujukan %s menunjuk bab lain tanpa menyebut babnya."
                      % m.group(0),
                      "Tulis \"Bab %s %s\" supaya pembaca tahu harus membuka "
                      "bab mana." % (m.group(1), m.group(0)),
                      m.group(0))
            ekor = teks.rstrip()[-14:]

    # 2. Bagian yang seluruhnya butir.
    judul_kini = (1, "(awal berkas)")
    n_butir = n_prosa = 0

    # Bagian yang memang berupa daftar menurut anatomi modul — ringkasan,
    # latihan, kerangka slide, referensi, daftar gambar — tidak dihitung.
    dikecualikan = [re.compile(p) for p in
                    ambang.get("butir_judul_dikecualikan", [])]

    def tutup_bagian():
        if any(rx.search(judul_kini[1]) for rx in dikecualikan):
            return
        if n_butir >= ambang["butir_minimum"]:
            rasio = n_butir / float(n_butir + n_prosa or 1)
            if rasio > ambang["butir_rasio_maks"]:
                catat(judul_kini[0], "butir-berlebih", "ringan",
                      "Bagian ini %d butir berbanding %d baris prosa."
                      % (n_butir, n_prosa),
                      "Ubah sebagian menjadi kalimat; butir yang tidak "
                      "berurut dan tidak sejajar lebih jelas sebagai prosa.",
                      judul_kini[1].strip())

    for nomor, teks, jenis in baris:
        if jenis == "judul":
            tutup_bagian()
            judul_kini = (nomor, teks)
            n_butir = n_prosa = 0
            if _ada_emoji(teks):
                catat(nomor, "emoji-judul", "berat",
                      "Emoji pada judul.",
                      "Hapus. Format mengikuti isi, bukan menghiasinya.",
                      teks.strip())
        elif jenis == "butir":
            n_butir += 1
        elif jenis == "prosa":
            n_prosa += 1
    tutup_bagian()

    # 3. Pembuka paragraf yang berulang.
    kumpulan = paragraf(baris)
    beruntun = []
    for par in kumpulan:
        awal = re.sub(r"[^a-z]", "", par[0][1].lower().split(" ")[0] or "")
        if beruntun and beruntun[-1][1] == awal and awal:
            beruntun.append((par[0][0], awal))
        else:
            if len(beruntun) >= ambang["pembuka_paragraf_berulang"]:
                catat(beruntun[0][0], "pembuka-berulang", "ringan",
                      "%d paragraf berturut-turut dibuka kata yang sama."
                      % len(beruntun),
                      "Ubah salah satunya; irama yang seragam terbaca mesin.",
                      beruntun[0][1])
            beruntun = [(par[0][0], awal)]
    if len(beruntun) >= ambang["pembuka_paragraf_berulang"]:
        catat(beruntun[0][0], "pembuka-berulang", "ringan",
              "%d paragraf berturut-turut dibuka kata yang sama."
              % len(beruntun),
              "Ubah salah satunya; irama yang seragam terbaca mesin.",
              beruntun[0][1])

    # 4. Penebalan yang ditaburkan, dan kalimat yang terlalu panjang.
    for par in kumpulan:
        gabung = " ".join(t for _, t in par)
        tebal = len(re.findall(r"\*\*[^*]+\*\*", gabung))
        if tebal > ambang["tebal_per_paragraf_maks"]:
            catat(par[0][0], "tebal-berlebih", "ringan",
                  "%d penebalan dalam satu paragraf." % tebal,
                  "Sisakan yang benar-benar menjadi kaitan mata pembaca.",
                  par[0][1].strip()[:60])
        for kalimat in re.split(r"(?<=[.!?])\s+", gabung):
            kata = _kata(kalimat)
            if len(kata) > ambang["kalimat_panjang_kata"]:
                catat(par[0][0], "kalimat-panjang", "ringan",
                      "Kalimat sepanjang %d kata." % len(kata),
                      "Pecah menjadi dua.",
                      " ".join(kata[:8]) + " …")
                break

    return temuan


def periksa(berkas, pola):
    baris = baca(berkas)
    if not baris:
        return []
    return periksa_leksikal(berkas, baris, pola) + \
        periksa_struktur(berkas, baris, pola)


def kumpulkan_sasaran():
    berkas = []
    for pola_glob in SASARAN:
        berkas.extend(sorted(AKAR_REPO.glob(pola_glob)))
    return [b for b in berkas if b.is_file()]


def laporkan(temuan, ringkas, berat_saja):
    urut = {"berat": 0, "ringan": 1}
    temuan.sort(key=lambda t: (str(t.berkas), t.baris, urut[t.bobot]))
    n_berat = 0
    berkas_kini = None

    for t in temuan:
        if berat_saja and t.bobot != "berat":
            continue
        if t.bobot == "berat":
            n_berat += 1
        try:
            nama = Path(t.berkas)
        except ValueError:
            nama = Path(t.berkas)
        if nama != berkas_kini:
            print("\n%s" % nama)
            berkas_kini = nama
        print("  %4d:%-3d %-7s %-20s %s"
              % (t.baris, t.kolom, t.bobot, t.kode, t.pesan))
        if not ringkas:
            print("           %-7s \"%s\"" % ("", t.kutipan))
            print("           %-7s %s" % ("", t.saran))
    return n_berat


def main(argv):
    # Konsol Windows masih berkodekan cp1252; tanpa ini tanda pisah pada pesan
    # aturan tercetak sebagai tanda tanya.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    ringkas = "--ringkas" in argv
    berat_saja = "--berat" in argv
    berkas_pola = POLA_BAKU
    if "--pola" in argv:
        berkas_pola = Path(argv[argv.index("--pola") + 1])

    sisa = [a for a in argv if not a.startswith("--")]
    if "--pola" in argv:
        sisa = [a for a in sisa if a != str(berkas_pola)]

    sasaran = kumpulkan_sasaran() if "--semua" in argv else \
        [Path(a) for a in sisa]
    if not sasaran:
        print("tidak ada berkas untuk diperiksa", file=sys.stderr)
        return 1

    pola = muat_pola(berkas_pola)
    semua = []
    for b in sasaran:
        semua.extend(periksa(b, pola))

    n_berat = laporkan(semua, ringkas, berat_saja)
    n_ringan = len([t for t in semua if t.bobot == "ringan"])
    print("\n%d berkas diperiksa, %d temuan berat, %d temuan ringan"
          % (len(sasaran), n_berat, n_ringan))
    return 1 if n_berat else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
