# Bab I – III: pendahuluan, tinjauan pustaka, metode

Untuk proposal, urutan menulis adalah **Bab III → Bab II → Bab I**. Untuk naskah akhir, ketiga
bab ini direvisi sesudah Bab IV selesai (tahap 4 di SKILL.md). Nama subbab mengikuti pedoman;
yang di bawah adalah fungsi tiap bagian, bukan judul wajib.

## Bab I Pendahuluan

Bab I harus membuat pembaca menerima tiga hal: masalahnya nyata, belum terjawab untuk konteks
ini, dan penelitian ini dapat menjawabnya.

| Bagian | Fungsinya | Kegagalan yang sering |
|---|---|---|
| Latar belakang | Dari kondisi seharusnya (aturan, standar, teori, target) ke kondisi nyata (data awal, observasi, laporan), lalu kesenjangan di antaranya, lalu apa yang sudah dan belum dilakukan penelitian sebelumnya | Dibuka dengan sejarah umum ("Di era globalisasi…"); masalah hanya diklaim tanpa bukti awal; penelitian terdahulu dicantumkan tanpa dikatakan apa kurangnya |
| Identifikasi / batasan masalah | Memilih bagian masalah yang diteliti dan menyebut yang tidak | Batasan yang sebenarnya keterbatasan waktu penulis, bukan pilihan ilmiah |
| Rumusan masalah | Pertanyaan yang dijawab oleh data; satu konsep per pertanyaan; dapat dijawab dengan metode di Bab III | "Bagaimana merancang…" tanpa ukuran keberhasilan; pertanyaan yang jawabannya ya/tidak; rumusan yang tidak muncul lagi di Bab V |
| Tujuan | Cermin rumusan, satu-satu, dengan kata kerja yang dapat diperiksa (menganalisis, mengukur, mengembangkan dan menguji) | Tujuan lebih banyak atau berbeda isi dari rumusan |
| Manfaat | Siapa yang memakai hasilnya dan untuk apa, teoretis dan praktis | Manfaat generik yang berlaku untuk penelitian apa pun |

Bukti awal di latar belakang adalah angka atau fakta yang bersumber: data instansi, hasil
pra-survei, observasi tercatat, laporan resmi. Bila belum ada, tulis
`[PERLU: data awal masalah — sumber?]`; jangan mengarang "berdasarkan observasi peneliti".

Untuk skripsi, kebaruan tidak wajib; cukup masalah nyata dan penyelesaian yang benar. Untuk
tesis dan disertasi, latar belakang harus menyebut karya terdekat dan apa yang ditambahkan
(lihat `scientific-article-writing/references/gap-from-limitations.md` untuk cara mencari celah
dari keterbatasan penelitian terdahulu).

## Bab II Tinjauan Pustaka

Bab II menyediakan apa yang dipakai Bab III dan Bab IV, tidak lebih. Ujinya sederhana: setiap
teori atau konsep di Bab II harus dipakai oleh salah satu dari: definisi operasional, instrumen,
model, standar pengujian, atau pembahasan Bab IV. Yang tidak dipakai, dibuang.

- **Kajian teori:** definisi dari sumber primer (buku teks, artikel asli), bukan dari skripsi
  lain atau blog. Satu konsep, satu definisi yang dipakai, alasan memilihnya bila ada beberapa.
- **Penelitian terdahulu:** dipilih yang paling dekat (variabel, metode, konteks sama), tidak
  sekadar banyak. Untuk tiap penelitian: apa yang dilakukan, apa hasilnya, apa bedanya dengan
  penelitian ini. Tabel boleh, tetapi kolom "perbedaan" wajib berisi, bukan "lokasi berbeda".
- **Kerangka berpikir:** alur dari masalah ke teori ke variabel/kategori ke hipotesis atau
  pertanyaan. Gambar harus sama dengan teks dan dengan model di Bab III.
- **Hipotesis (kuantitatif):** satu hipotesis per hubungan yang diuji, diturunkan dari teori
  dan penelitian terdahulu yang baru disebut, dapat diuji dengan analisis yang direncanakan.

Setiap sitasi berasal dari metadata yang diambil atau dari PDF yang dibaca. Kutipan langsung
memakai nomor halaman. Sitasi yang belum diperiksa: `[PERLU: verifikasi sitasi]`. Daftar pustaka
dicek dengan `research-integrity/scripts/verify_references.py`.

Kegagalan yang sering: bab yang berisi rangkuman buku teks per variabel tanpa kaitan; definisi
dari tiga sumber yang saling bertentangan tanpa dipilih; penelitian terdahulu yang tidak
pernah disebut lagi di pembahasan; kutipan berantai ("Sutabri dalam Andi, 2020") untuk sumber
yang mudah diperoleh.

## Bab III Metode Penelitian

Bab III harus cukup rinci sehingga orang lain dapat mengulang penelitian dan pembimbing dapat
menilai apakah metode itu menjawab rumusan. Isi minimal menurut jalur: `jalur-metode.md`.

Yang selalu ada:

1. Desain dan alasannya — mengapa desain ini menjawab rumusan, bukan definisi desain dari buku.
2. Tempat dan waktu, atau sumber data sekunder (nama, periode, cara akses, lisensi).
3. Subjek: populasi-sampel dengan cara penentuan jumlah, atau informan dengan kriteria
   pemilihan, atau pengguna/penguji untuk R&D.
4. Variabel/fokus dengan definisi operasional atau deskripsi fokus yang dapat diamati.
5. Instrumen dan bukti kualitasnya (validitas-reliabilitas, validasi ahli, pedoman wawancara).
6. Prosedur pengumpulan data, berurutan.
7. Teknik analisis yang dipetakan ke tiap rumusan (tabel rumusan → data → analisis membantu).
8. Etika: persetujuan responden, izin instansi, anonimisasi, bila relevan.

Di naskah akhir, Bab III ditulis dalam bentuk lampau dan **sesuai yang benar-benar dilakukan**.
Perubahan dari proposal (jumlah sampel tercapai, instrumen direvisi, informan bertambah) ditulis
terang dengan alasannya, bukan disamarkan.

Kegagalan yang sering: rumus Slovin tanpa populasi yang jelas atau dengan sampel yang tidak
tercapai; "teknik purposive" tanpa kriteria; uji validitas yang disebut tetapi hasilnya tidak
pernah dilaporkan; analisis yang tidak dapat menjawab rumusan (deskriptif untuk pertanyaan
pengaruh); metode pengembangan perangkat lunak disebut tetapi tahapnya tidak muncul di Bab IV.

## Khusus proposal

- Bab I–III ditulis dalam bentuk rencana ("akan"), Bab III paling rinci.
- Hipotesis dan kerangka berpikir sudah final; perubahannya nanti harus dijelaskan.
- Instrumen dilampirkan (kuesioner, pedoman wawancara, rancangan pengujian), karena itulah yang
  dinilai pada seminar proposal.
- Jadwal dan anggaran mengikuti format pedoman, bila diminta.
- Sebelum seminar proposal, jalankan `thesis-audit` dengan `--level` yang sesuai: rantai
  rumusan ↔ tujuan sudah dapat diaudit walaupun Bab IV–V belum ada (modul tersebut akan berstatus
  `not_assessable`, bukan gagal).
