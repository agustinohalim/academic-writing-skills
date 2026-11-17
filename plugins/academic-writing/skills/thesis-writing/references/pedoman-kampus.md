# Profil tugas dari pedoman kampus

Pedoman penulisan fakultas (atau program studi) adalah aturan yang berlaku. Instruksi tertulis
pembimbing biasanya mengalahkan pedoman untuk hal yang ia tetapkan; bila keduanya bertentangan,
tanyakan, jangan memilih sendiri. Skill ini tidak menyimpan pedoman kampus mana pun — nilai di
bawah adalah **bawaan untuk dikonfirmasi**, bukan aturan.

## Cara mengisi

1. Minta berkas pedoman (PDF/DOCX) dan, bila ada, contoh skripsi yang sudah disetujui dari prodi
   yang sama. Contoh skripsi menunjukkan praktik yang sebenarnya dipakai; pedoman menunjukkan aturan.
2. Isi tabel variabel di bawah. Setiap nilai diberi asal: `pedoman hlm. N`, `contoh skripsi`,
   `instruksi pembimbing`, atau `bawaan — [PERLU: pedoman]`.
3. Tunjukkan profil kepada penulis sebelum bab pertama ditulis. Simpan sebagai `PROFIL.md` di
   folder naskah agar dipakai lagi di setiap giliran dan oleh skrip ekspor.

Nilai tanpa asal tidak boleh muncul. Lebih baik `[PERLU: pedoman]` daripada tebakan yang terlihat
pasti.

## Variabel struktur

| Variabel | Yang dicari di pedoman | Bawaan umum (konfirmasi) |
|---|---|---|
| Jenjang dan jenis | skripsi / tesis / disertasi; proposal atau naskah akhir | — wajib diisi |
| Jenis penelitian yang diakui | kuantitatif, kualitatif, R&D, campuran, studi kasus, rancang bangun | sesuai prodi |
| Nama dan urutan bab | Bab I Pendahuluan … Bab V Penutup; ada prodi yang memakai enam bab atau bab "Analisis dan Perancangan" | I Pendahuluan, II Tinjauan Pustaka, III Metode Penelitian, IV Hasil dan Pembahasan, V Kesimpulan dan Saran |
| Isi Bab I | latar belakang, identifikasi/batasan masalah, rumusan, tujuan, manfaat, sistematika | semua kecuali sistematika sering dihapus di pedoman baru |
| Isi Bab II | kajian teori, penelitian terdahulu (tabel?), kerangka berpikir, hipotesis | hipotesis di Bab II untuk kuantitatif |
| Isi Bab III | desain, lokasi/waktu, populasi-sampel atau subjek/informan, variabel dan definisi operasional, instrumen, teknik pengumpulan, teknik analisis, prosedur | sesuai jalur metode |
| Proposal | bab yang diminta (biasanya I–III), jadwal, rencana anggaran | Bab I–III + daftar pustaka |
| Bagian awal | sampul, halaman judul, pengesahan, pernyataan keaslian, prakata, abstrak dua bahasa, daftar isi/tabel/gambar/lampiran | ikuti urutan pedoman |
| Abstrak | panjang (kata), struktur, kata kunci (jumlah), bahasa | 150–250 kata, 3–5 kata kunci, Indonesia + Inggris |
| Gaya sitasi | APA (edisi), IEEE, Harvard, Vancouver, catatan kaki | APA 7 |
| Penulisan "dkk." / "et al." | kapan dipakai (≥ 3 penulis?) | APA 7: "dkk." sejak penulis ketiga |
| Batas umur pustaka | 5 atau 10 tahun; proporsi jurnal | 10 tahun, ≥ 60–80% artikel jurnal |
| Penomoran judul | BAB I / 1.1 / 1.1.1 atau A, B, 1, a | BAB I, 1.1, 1.1.1 |
| Tabel dan gambar | nomor per bab (Tabel 4.2), letak judul (tabel di atas, gambar di bawah), sumber | per bab, judul tabel di atas, gambar di bawah |
| Pernyataan penggunaan AI | wajib/tidak, letaknya | `[PERLU: pedoman]` — banyak pedoman belum mengatur |

## Variabel format (dipakai skrip ekspor)

| Variabel | Bawaan umum (konfirmasi) | Argumen `ekspor_naskah.py` |
|---|---|---|
| Ukuran kertas | A4 (21 × 29,7 cm), kadang A4 70/80 g | selalu A4 |
| Margin kiri-atas-kanan-bawah | 4 – 4 – 3 – 3 cm (variasi umum: 4-3-3-3) | `--margin 4 4 3 3` |
| Huruf | Times New Roman | `--font "Times New Roman"` |
| Ukuran huruf isi | 12 pt | `--ukuran 12` |
| Spasi isi | 1,5 (variasi umum: 2) | `--spasi 1.5` |
| Spasi abstrak, kutipan blok, judul tabel, daftar pustaka | 1 | atur manual di DOCX |
| Nomor halaman | romawi kecil untuk bagian awal, arab mulai Bab I; letak berbeda di halaman awal bab | atur manual di DOCX |
| Indentasi paragraf | 1–1,25 cm baris pertama | gaya "Body Text" di DOCX |

Hal yang tidak dapat dikerjakan Markdown/pandoc dengan rapi — nomor halaman romawi lalu arab,
halaman pengesahan bertanda tangan, sampul berlogo — dikerjakan sekali di DOCX hasil ekspor, atau
dengan templat DOCX dari prodi sebagai `--templat`. Catat langkah manual itu di `PROFIL.md`
supaya tidak terlupa pada ekspor berikutnya.

## Bila tidak ada pedoman

Pakai bawaan di atas, tandai **setiap** nilai `bawaan — [PERLU: pedoman]`, dan katakan kepada
penulis bahwa format akhir mengikuti pedoman prodi, bukan skill ini. Jangan mengutip "aturan
kampus X" dari ingatan; pedoman berubah tiap beberapa tahun dan berbeda antarprodi dalam satu
kampus.
