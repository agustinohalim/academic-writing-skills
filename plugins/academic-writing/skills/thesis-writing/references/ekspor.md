# Ekspor ke DOCX, PDF, dan LaTeX

Bab-bab Markdown adalah sumber; DOCX, PDF, dan LaTeX adalah hasil ekspor. Revisi dilakukan di Markdown,
lalu ekspor ulang. Bila pembimbing memberi komentar di DOCX, pindahkan perubahannya ke Markdown
— jangan menyunting dua sumber.

## Kebutuhan

| Untuk | Perlu | Cek |
|---|---|---|
| DOCX | [pandoc](https://pandoc.org) | `pandoc --version` |
| PDF (disarankan) | LibreOffice — PDF dibuat dari DOCX yang sama, jadi formatnya identik | `soffice --version` |
| PDF (alternatif) | Typst atau mesin LaTeX (`xelatex`) untuk `pandoc --pdf-engine` | `typst --version`, `xelatex --version` |
| LaTeX (`.tex`) | pandoc saja; mengompilasi `.tex` perlu distribusi TeX (TeX Live, MiKTeX) atau Overleaf | — |
| Sitasi otomatis | berkas `.bib` (ekspor dari Zotero/Mendeley) dan berkas `.csl` gaya sitasi | — |

Skrip mencari mesin PDF dalam urutan LibreOffice → Typst → xelatex dan berhenti dengan pesan
jelas bila tidak ada satu pun.

## Pemakaian

```bash
# satu folder: semua .md diurutkan menurut nama (00_awal.md, bab_1.md, bab_2.md, ...)
python ekspor_naskah.py bab/ --out Skripsi_Budi --docx --pdf

# berkas tertentu, sesuai urutan yang diberikan
python ekspor_naskah.py bab_1.md bab_2.md bab_3.md --out Proposal_Budi --docx

# format dari profil tugas
python ekspor_naskah.py bab/ --out Skripsi --docx --margin 4 3 3 3 --spasi 2 --font "Times New Roman" --ukuran 12

# sitasi dari Zotero (Better BibTeX) dengan gaya APA 7
python ekspor_naskah.py bab/ --out Skripsi --docx --bib pustaka.bib --csl apa.csl

# templat DOCX dari prodi menggantikan templat yang dibuat skrip
python ekspor_naskah.py bab/ --out Skripsi --docx --templat templat_prodi.docx

# draf untuk pembimbing, penanda [PERLU: ...] dibiarkan
python ekspor_naskah.py bab/ --out Draf_Bab4 --docx --draft

# LaTeX mandiri (kelas report, BAB menjadi \chapter), .bib disalin ke samping .tex
python ekspor_naskah.py bab/ --out Skripsi --latex --bib pustaka.bib

# isi saja, untuk ditempel ke templat LaTeX kampus atau kelas jurnal (elsarticle, sn-jnl, IEEEtran)
python ekspor_naskah.py manuscript.md --out paper --latex-body --bib refs.bib --lang en --auto-number
```

Urutan folder diambil dari nama berkas dengan angka dibandingkan sebagai angka, jadi `bab_10.md`
datang sesudah `bab_9.md`. Berkas yang namanya diawali `_` atau `.` dilewati (catatan pribadi).

Argumen format: `--margin KIRI ATAS KANAN BAWAH` dalam cm (bawaan 4 4 3 3), `--font` (bawaan
Times New Roman), `--ukuran` dalam pt (bawaan 12), `--spasi` (bawaan 1.5). Ukuran kertas selalu A4.
Nilai-nilai ini harus sama dengan profil tugas (`pedoman-kampus.md`); bawaan bukan aturan kampus.
`--lang id|en` (bawaan `id`) masuk ke semua format: bahasa pemeriksa ejaan Word, istilah sitasi
("dan", bukan "and"), dan babel di LaTeX.

## LaTeX

- `--latex` menulis `.tex` mandiri: A4, margin, ukuran huruf (10/11/12 pt), spasi, bahasa.
  Kelas bawaan `report`, sehingga setiap `#` menjadi `\chapter`; `--kelas article` untuk artikel.
- `--latex-body` menulis isi tanpa preambul, untuk ditempel ke templat kampus atau kelas jurnal
  yang sudah mengatur halaman, huruf, dan gaya pustaka.
- Dengan `--bib`, kunci sitasi dipertahankan (`\citep`, `\citet` lewat natbib, bawaan; atau
  `--cite biblatex`) dan `.bib` disalin ke folder keluaran, karena jurnal meminta `.tex` + `.bib`.
  `--cite citeproc` merender sitasi menjadi teks seperti di DOCX.
- Gaya pustaka natbib bawaan pandoc adalah `plainnat`; ganti `\bibliographystyle{...}` dengan
  gaya kampus atau `.bst` jurnal.
- Gambar tetap ditautkan dengan jalurnya; salin folder gambar ke samping `.tex` sebelum
  mengompilasi atau mengunggah ke Overleaf.

## Penanda yang tersisa

Sebelum mengekspor, skrip memindai `⬜`, `[PERLU …]`, `TODO`, `XX`, dan `???`. Bila ada, ekspor
ditolak dan setiap penanda dicetak dengan berkas dan nomor barisnya. `--draft` mengizinkan
ekspor untuk draf bimbingan; naskah untuk seminar atau sidang diekspor tanpa `--draft`.

## Apa yang diatur skrip, apa yang tidak

Skrip membuat `reference.docx` dari templat bawaan pandoc lalu mengubahnya: kertas A4, margin,
huruf pada semua gaya, ukuran huruf, spasi baris, dan warna judul dihapus (judul hitam).
Gaya judul pandoc (Heading 1–3) dipakai untuk BAB dan subbab, sehingga daftar isi dapat dibuat
otomatis di Word (References → Table of Contents).

Yang tetap dikerjakan manual di DOCX, sekali sebelum dicetak: sampul dan halaman pengesahan,
nomor halaman romawi lalu arab, judul BAB di tengah halaman baru bila pedoman memintanya,
spasi tunggal untuk abstrak dan daftar pustaka, lampiran berukuran lain. Untuk menghindari
pekerjaan berulang, simpan DOCX yang sudah dirapikan sebagai templat prodi dan pakai `--templat`.

## Penulisan Markdown yang aman untuk ekspor

- Satu `#` per BAB (`# BAB I PENDAHULUAN`), `##` untuk 1.1, `###` untuk 1.1.1. Nomor ditulis
  sendiri; pandoc tidak menomori judul kecuali diminta.
- Tabel pipa Markdown untuk tabel sederhana; tabel kompleks (sel gabung) lebih baik disusun di
  DOCX atau disisipkan sebagai gambar dengan data aslinya di lampiran.
- Gambar: `![Gambar 3.1 Kerangka berpikir](gambar/kerangka.png)`; keterangan diambil dari teks
  dalam kurung siku. Jalur gambar boleh relatif terhadap folder bab.
- Nomor tabel dan gambar ditulis sendiri per bab di keterangan (`: Tabel 2.1 Penelitian
  terdahulu` di bawah tabel). PDF dan LaTeX mandiri mematikan label otomatis mesinnya, jadi
  keterangan tercetak persis seperti ditulis dan cocok dengan rujukan di teks yang diperiksa
  `thesis-audit`. Untuk artikel jurnal, tulis keterangan tanpa nomor dan pakai `--auto-number`.
- Daftar pustaka dengan `--bib` dan citeproc: letakkan di berkas terakhir
  `# DAFTAR PUSTAKA` diikuti `::: {#refs}` dan `:::` agar muncul di bawah judulnya sendiri.
- Sitasi pandoc: `[@sutabri2012]`, `[@pressman2019, hlm. 45]`, atau naratif `@sutabri2012`.
  Tanpa `--bib`, tulis sitasi biasa (Sutabri, 2012) dan daftar pustaka secara manual.
- Pemisah halaman antar-BAB: skrip menyisipkan pemisah halaman sebelum setiap berkas kecuali
  yang pertama.
