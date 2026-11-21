# Rencana Konten Orisinal + Perbaikan Kesiapan AdSense — NusaTrance

**STATUS 21 Nov 2026 (dikerjakan):** batch 1 selesai. 6 artikel di
`data-artikel.json` (tervalidasi); semua perbaikan butir 4.1-4.10
diterapkan ke `build-v88/nusatrance-site/index.html` + `sitemap.xml` +
`robots.txt` + `tentang/index.html`; verifikasi lokal lulus
(`node --check`, 14 assert logika, serve + curl 7 URL 200).
Yang masih menunggu Muhammad: ZIP deploy (butir 5a), push JSON
`data-artikel.json` + `data-redaksi.json` (butir 5b), keputusan terbuka
(butir 5c), dan kadensi harian seminggu (butir 5d). JANGAN klik Resubmit
AdSense sebelum ZIP ter-deploy dan artikel tampil live.

Ditulis 21 November 2026. Keputusan Muhammad 21 Nov 09:05: fokus rubrik
Edukasi dan Hobi, isi dengan konten orisinal kita (pengetahuan + tips dan
trik), bukan sekadar mengumpulkan berita. Update harian selama seminggu,
lalu resubmit AdSense. Suara harus seperti manusia asli, bukan AI.

## 1. Diagnosis: kenapa situs belum siap AdSense

Audit live 21 Nov 08:59-09:03 + pemeriksaan kode situs 21 Nov (build v88)
menemukan dua kelompok masalah. Kelompok pertama adalah halaman yang
sudah ada sebagai berkas tapi tidak terhubung, kelompok kedua adalah isi
dan logika situs.

### 1a. Halaman kebijakan SUDAH ADA sebagai berkas, tapi tidak ter-link

Folder deploy sudah berisi halaman beneran sejak 14-15 Nov:

- `/privasi/` — Kebijakan Privasi lengkap, menyebut cookie Google AdSense
  dan cara menonaktifkan personalisasi iklan lewat Pengaturan Iklan Google.
- `/kontak/` — Kontak Redaksi, email farmatrance@gmail.com + sosmed.
- `/tentang/` — Tentang Kami lengkap.
- `/syarat-ketentuan/` — Syarat dan Ketentuan lengkap.

Audit tidak menemukannya karena TIDAK ADA satu pun tautan ke keempat halaman
itu di homepage (header, footer, menu pembaca, dialog Tentang). Perbaikannya
bukan membuat halaman baru, melainkan menautkan yang sudah ada dari footer
(lihat butir 4.1). Sitemap juga perlu diperbaiki: masih memakai domain
nusatrance.pages.dev (bukan www.nusatrance.web.id) dan belum mencantumkan
/syarat-ketentuan/.

### 1b. Cacat yang ditemukan di kode (build v88, index.html)

| # | Cacat | Penyebab di kode | Perbaikan |
|---|-------|------------------|-----------|
| 1 | Tidak ada penulis bernama di artikel mana pun | Pembaca artikel (reader) tidak punya elemen byline; data berita tidak punya field penulis | Tambah elemen byline di reader + isi dari data (butir 4.4) |
| 2 | Atribusi sumber tidak konsisten; artikel headline (Wapres, Bitcoin) tidak menampilkan "Sumber" sama sekali | Item headline di data-berita.json tidak punya field source/sourceUrl; reader menyembunyikan baris sumber bila sourceUrl kosong | Situs menyalin source dari item kategori kembar dengan slug sama (butir 4.5); cron diminta menambah source ke headline (butir 6.2) |
| 3 | Paragraf atribusi mengarang tanggal: "Liputan lengkap berita ini diterbitkan oleh X pada [tanggal edisi]" | ensureArticle + renderCategories memakai tanggal edisi sebagai tanggal terbit sumber | Ganti kalimatnya dengan atribusi tanpa tanggal (butir 4.5) |
| 4 | Tanggal ganda "21 Nov 2026 2026" di kartu | cardDate() menempel tahun edisi ke field time yang sudah berisi tahun | Perbaiki cardDate: jangan tempel tahun bila time sudah berakhiran tahun (butir 4.6) |
| 5 | Badge reader "Sabtu, 14 Nov 2026, Edisi Pagi" + tanda tangan artikel selalu 14 Nov | Teks hardcoded di markup reader (pill ghost) dan di openArticle (sign-off) | Jadikan dinamis dari tanggal artikel/edisi (butir 4.6) |
| 6 | Judul seksi Politik muncul dua kali; Religi berisi festival budaya; Edukasi berisi sains | renderCategories + arcCat memetakan ulang label: Hukum jadi Politik, Budaya jadi Religi, Sains jadi Edukasi, Nasional jadi Entertainment | Hapus pemetaan ulang; render label asli data (butir 4.2) |
| 7 | Filter Hobi mengembalikan artikel hukum (Duta Palma) | SCOPES Hobi memakai pencocokan kata kunci substring ("panen" cocok di artikel sawit) | Hobi jadi kategori beneran (cats, bukan keys) setelah ada data-artikel.json (butir 4.3) |
| 8 | Filter/pencarian kosong membuat seksi tampil sebagai judul tanpa kartu | applyFilter hanya menyembunyikan kartu, bukan blok seksinya | Sembunyikan blok seksi yang semua kartunya tersaring (butir 4.7) |
| 9 | Tombol Store + Marketplace mati | disabled atas perintah pemilik 16 Nov 2026 (dua entitas bisnis tidak boleh saling taut) | Tetap tanpa tautan, tapi beri perilaku jujur: dialog "Segera hadir" (butir 4.8) |
| 10 | Dialog Pasang Iklan menampilkan angka "—" (kunjungan, pengikut, pembaca buletin) | Tidak ada data audiens nyata | Sembunyikan tiga blok angka sampai ada datanya; jangan karang angka (butir 4.9) |
| 11 | Hampir semua artikel "3 mnt baca" | Pipeline menulis "3 mnt baca" untuk semua item | Artikel orisinal menyimpan readMinutes hasil hitung kata/200; pipeline berita diminta menghitung juga (butir 6.2) |
| 12 | Ilustrasi generik tak terkait isi (skyline Jakarta untuk laga di Yangon) | Pembaca artikel memakai CAT_IMG[kategori], bukan img item dari pool | Pakai it.img (pool) bila ada, baru fallback ke ilustrasi kategori (butir 4.5) |
| 13 | Rubrik Edukasi dan Hobi kosong/tipis | data-berita.json tidak punya kunci Edukasi/Hobi; keduanya hanya filter kata kunci atas berita | Sistem artikel orisinal data-artikel.json (butir 2 dan 3) |
| 14 | Ekor kategori basi dan salah kategori (Entertainment berisi siklon/crane/cuaca 14 Nov) | Cron hanya memangkas kategori bila melebihi 8 item; ekor lama bertahan | Cron diminta mengganti item lebih dari 7 hari saat menyisipkan yang segar (butir 6.2) |

Catatan soal badge edisi "14 Nov" di homepage: badge itu dibaca dari
data.edition.date di data-berita.json (bukan hardcoded). Bila situs live
masih menampilkan 14 Nov, penyebabnya adalah data GitHub yang belum
di-push edisi terbarunya, bukan template. Template hanya memakai tanggal
14 Nov sebagai fallback saat fetch gagal. Fallback tertanam (FALLBACK_DATA)
wajib disegarkan ke edisi terbaru setiap kali ZIP baru dibangun.

## 2. Analisis overwrite: apa yang ditimpa rebuild carousel 2x sehari

Cron carousel pagi (05:30) dan malam (18:00), langkah 7c, MENULIS ULANG
data-berita.json dari nol setiap edisi:

- edition diganti edisi baru; ticker diganti 8 string baru; headlines
  diganti 8 item baru (tanpa source/sourceUrl).
- categories: tiap berita edisi disisipkan di URUTAN PERTAMA kategorinya;
  bila kategori melebihi 8 item, item terakhir dihapus. Kategori lain
  "tidak disentuh", tapi karena berkas ditulis ulang penuh, kunci yang
  tidak disalin ulang oleh worker akan hilang.
- videos disalin dari berkas lama lalu diperbarui.
- append_edition.py (langkah 7c b4) hanya menambah ke koleksi-berita.json
  (append-only, dedupe slug) dan meregenerasi data-arsip.json +
  data-trending.json. Skrip ini TIDAK menyentuh data-berita.json.
- File yang TIDAK PERNAH disentuh cron: data-artikel.json (baru),
  data-redaksi.json (baru), pool-gambar.json (hanya ditambah),
  RENCANA-KONTEN-ORISINAL.md (berkas ini).

### Kesimpulan desain

Artikel orisinal TIDAK BOLEH tinggal di data-berita.json. Alasannya:

1. Berkas itu ditulis ulang tiap edisi; satu kelalaian worker menghapus
   semua artikel.
2. Siklus hidupnya beda: berita bersifat sementara dan dinilai skor tiap
   edisi; artikel bersifat evergreen, berpenulis, bertanggal terbit, dan
   ber-URL tetap.
3. Aturan cap 8 item dan anti-dobel berita tidak berlaku untuk artikel.
4. Isi artikel (400-600 kata) akan menggelembungkan data-berita.json yang
   sudah ~920 KB.

Karena itu artikel tinggal di berkas terpisah, `data-artikel.json`, yang
dibaca situs seperti data-berita.json (fetch dari GitHub raw, fallback
tertahan bila gagal). Cron tidak pernah menyentuhnya. Update harian =
tambah artikel ke berkas itu + push (agen utama) — tanpa deploy.

## 3. Sistem artikel orisinal

### 3.1 data-artikel.json

Lokasi: `~/workspace/nusatrance-data/data-artikel.json` (repo
DzeusSxMonstera/nusatrance-data, branch main). Situs mengambilnya dari
`https://raw.githubusercontent.com/DzeusSxMonstera/nusatrance-data/main/data-artikel.json`.

Skema per artikel:

```json
{
  "version": 1,
  "updated": "2026-11-21",
  "source_note": "Artikel orisinal Redaksi NusaTrance. Bukan ringkasan berita. Ditulis dan diperiksa redaksi; angka dan klaim faktual hanya yang terverifikasi.",
  "articles": [
    {
      "slug": "cara-membaca-berita-biar-tidak-kena-hoaks",
      "title": "Cara Membaca Berita Biar Tidak Gampang Kena Hoaks",
      "excerpt": "Satu-dua kalimat ringkasan.",
      "category": "Edukasi",
      "author": "Redaksi NusaTrance",
      "date": "2026-11-21",
      "dateLabel": "21 November 2026",
      "readMinutes": 3,
      "tags": ["literasi media", "hoaks"],
      "body": ["Paragraf pertama...", "Paragraf kedua..."]
    }
  ]
}
```

Aturan isi:

- Kategori hanya "Edukasi" atau "Hobi" (tahap ini).
- 400-600 kata per artikel (hitung kata body, tanpa judul/excerpt).
- readMinutes = ceil(jumlah kata / 200), minimal 1.
- body = array paragraf teks polos (tanpa HTML); situs merender tiap
  paragraf sebagai elemen p. Paragraf pertama jadi lead.
- author: "Redaksi NusaTrance" sampai Muhammad memutuskan model byline
  (butir 7.1). Field ini sudah disiapkan untuk nama penulis per artikel.
- img: tidak ada di batch awal; pembaca memakai ilustrasi kategori
  (CAT_IMG) sebagai fallback. Foto/ilustrasi per artikel bisa ditambah
  belakangan sebagai field img (URL pool) tanpa mengubah skema.
- Slug unik, huruf kecil, strip, tanpa tanggal di slug (URL tetap).

### 3.2 data-redaksi.json

Lokasi: `~/workspace/nusatrance-data/data-redaksi.json`. Sumber kebenaran
info redaksi: nama media, kota (Banjarmasin, Kalimantan Selatan), email
redaksi (farmatrance@gmail.com, sudah dipakai halaman Kontak), akun
sosmed, dan defaultAuthor untuk byline berita ("Redaksi NusaTrance").
Situs membacanya untuk byline default; bila fetch gagal, fallback ke
"Redaksi NusaTrance". Penamaan pendiri di berkas ini berstatus DRAF
sampai Muhammad menyetujui (butir 7.1).

### 3.3 Cara situs menampilkan artikel

- Fetch data-artikel.json bersamaan dengan data-berita.json (fungsi baru
  loadRemoteArticles, pola sama seperti loadRemoteData: timeout 4,5 detik,
  gagal = tampilkan berita saja, tanpa error ke pembaca).
- Artikel digabung ke renderCategories sebagai kategori "Edukasi" dan
  "Hobi" (artikel terbaru dulu), dan didaftarkan ke pool ARTICLES supaya
  bisa dibuka di pembaca artikel, dicari, dan difilter seperti berita.
- Artikel TIDAK masuk pool Sorotan/Featured/Latest/Other Posts (itu
  seksi berita) dan TIDAK masuk arsip berita (arsip adalah berita).
- Baris artikel di seksi kategori memakai excerpt + tanggal terbit +
  readMinutes hasil hitung, bukan "3 mnt baca".
- Pembaca artikel menampilkan: pil kategori, judul, byline (penulis +
  tanggal terbit + waktu baca), gambar (ilustrasi kategori bila belum
  ada foto), isi penuh, tanda tangan redaksi dengan tanggal artikel,
  dan artikel terkait. Tidak ada baris "Sumber" untuk artikel orisinal
  (bukan saduran); sebagai gantinya tanda tangan menyebut artikel asli
  Redaksi NusaTrance.
- Filter: tab Edukasi memakai cats ["Edukasi", "Sains"], tab Hobi memakai
  cats ["Hobi"] (bukan lagi kata kunci). Sub-item dropdown (Sekolah,
  Kuliah, Game, Fotografi, dst.) tetap memakai kata kunci seperti dulu.

### 3.4 Standar penulisan (wajib)

Empat skill dibaca dan diterapkan ke setiap artikel: local-anti-slop,
local-anti-slop-copywriting, local-humanize-writing, local-hook-viral.
Ringkasnya: tanpa em dash; tanpa pembuka "di era digital..."; tanpa
rule of three paksa; tanpa klaim/angka/kutipan/testimoni karangan;
kalimat pembuka konkret dan spesifik; panjang kalimat bervariasi; satu
gagasan per artikel; hook dibayar lunas di penutup. Setiap artikel
melewati audit dua pertanyaan skill copywriting sebelum dikirim:
"Apa yang membuat ini jelas buatan AI?" dan "Apakah ada fakta/angka/
tanggal/sitasi yang tidak ada di sumber?".

## 4. Perbaikan struktural situs (build v88)

Berkas kerja: `~/workspace/deploy/nusatrance/build-v88/nusatrance-site/index.html`
(21 MB, sebagian besar base64 gambar). Semua edit bersifat bedah kecil
dengan jangkar teks unik, tidak menyentuh blob base64. Halaman kebijakan
di folder yang sama (privasi/kontak/tentang/syarat-ketentuan/index.html)
masing-masing ~79 KB.

### 4.1 Tautkan halaman kebijakan dari footer (P0, AdSense)

Footer saat ini hanya punya: News, Featured Posts, Latest Posts,
Other Posts, dan tombol "Tentang Kami" yang membuka dialog. Perbaikan:

- Ubah tombol aboutFooterBtn menjadi tautan beneran ke /tentang/.
- Tambah tautan: Kontak (/kontak/), Privasi (/privasi/),
  Syarat dan Ketentuan (/syarat-ketentuan/).
- Perbarui sitemap.xml: domain jadi https://www.nusatrance.web.id/,
  tambah /syarat-ketentuan/, lastmod 2026-11-21. robots.txt: URL
  sitemap ikut diganti ke domain yang sama.

### 4.2 Hapus pemetaan ulang kategori (P0)

Di renderCategories dan arcCat, hapus baris pemetaan:

```js
var cat = rawCat === "Nasional" ? "Entertainment" : (rawCat === "Hukum" ? "Politik" : (rawCat === "Budaya" ? "Religi" : (rawCat === "Sains" ? "Edukasi" : rawCat)));
```

Ganti dengan `var cat = rawCat;` di kedua tempat. Dampak: seksi tampil
dengan label asli (Politik, Hukum, Budaya, Sains, Bencana, Peristiwa),
duplikat Politik hilang, Religi tidak lagi berisi festival budaya dengan
label salah. Tambah entri CAT_PILL untuk Bencana, Peristiwa, Hobi, Sains,
Budaya, dan CAT_IMG untuk Hobi, Bencana, Peristiwa (pakai ulang ilustrasi
kategori yang sudah ada lewat penugasan setelah definisi, supaya tidak
menyentuh blob base64).

### 4.3 Hobi jadi kategori beneran (P0)

SCOPES["Hobi"] dari keys menjadi `cats: ["Hobi"]`. SCOPES["Edukasi"]
sudah cats ["Edukasi", "Sains"] dan tidak berubah. Sub-item dropdown
Hobi/Edukasi tetap memakai kata kunci.

### 4.4 Byline penulis + tanggal terbit di pembaca artikel (P0)

Markup reader saat ini: pil kategori, pil edisi hardcoded, judul,
baris meta "@nusatrance · Redaksi NusaTrance · waktu baca". Perbaikan:

- Tambah baris byline di bawah judul: penulis (span id rAuthor) +
  tanggal terbit (span id rDate) + waktu baca (rRead yang sudah ada).
- openArticle mengisi rAuthor dari a.author (default "Redaksi
  NusaTrance") dan rDate dari a.date (tanggal artikel; untuk berita,
  tanggal edisi).
- Pil edisi diberi id rEdition dan diisi dinamis (tanggal edisi +
  label, atau tanggal artikel untuk artikel orisinal).
- Tanda tangan akhir artikel memakai tanggal artikel, bukan tanggal
  hardcoded 14 Nov 2026.
- CATATAN: model byline (nama orang vs kolektif) masih keputusan
  terbuka (butir 7.1). Mekanismenya sudah mendukung nama per artikel.

### 4.5 Atribusi sumber yang konsisten (P0)

- ensureArticle + renderCategories: ganti paragraf kedua yang mengarang
  tanggal terbit sumber menjadi: "Ringkasan ini disusun Redaksi
  NusaTrance dari liputan [sumber]. Baca laporan lengkapnya lewat
  tautan sumber di atas." Tanpa tanggal.
- Saat mendaftarkan artikel headline: bila headline tidak punya
  source/sourceUrl, salin dari item kategori kembar dengan slug sama.
- Pembaca artikel: pakai it.img (gambar pool) bila ada; bila tidak ada,
  baru ilustrasi kategori CAT_IMG. Caption disesuaikan (bukan lagi
  selalu "Ilustrasi berita [kategori]").

### 4.6 Perbaiki cacat tanggal (P1)

- cardDate: bila it.time sudah berakhiran tahun 4 digit, kembalikan
  apa adanya; jangan tempel tahun edisi. Fallback "14 Nov" diganti
  tanggal edisi (data.edition.date) bila time kosong.
- Pil edisi + tanda tangan reader: dinamis (butir 4.4).
- FALLBACK_DATA: disegarkan ke edisi terbaru setiap kali ZIP baru
  dibangun (catatan build, bukan edit kode).

### 4.7 Seksi kosong saat filter/pencarian (P1)

applyFilter: sesudah menyembunyikan kartu, sembunyikan juga blok seksi
(.cat-block, #featured, #latest, #other, wadah Sorotan) yang semua
kartu [data-search]-nya tersembunyi. Bila filter dibersihkan, semua
blok tampil lagi. Judul seksi tidak lagi tampil sendirian tanpa kartu.

### 4.8 Tombol Store + Marketplace (P1)

Tetap TANPA tautan (perintah pemilik 16 Nov 2026, dua entitas bisnis
tidak boleh saling taut). Supaya bukan kontrol mati: hapus atribut
disabled, tambahkan dialog kecil "Segera hadir" memakai sistem modal
yang sudah ada (openModal/closeModal + elemen .modal): teks jujur
bahwa toko NusaTrance masih disiapkan, tanpa tautan ke mana pun.
Wording dialog ada di butir 7.3 (butuh OK Muhammad bila mau diubah).

### 4.9 Angka "—" di Pasang Iklan (P1)

Sembunyikan tiga blok statistik (kunjungan situs per bulan, pengikut
sosmed, pembaca buletin) sampai ada data nyata. Baris "Hubungi redaksi
untuk data audiens terbaru sebelum memesan." tetap tampil. Jangan
karang angka.

### 4.10 Waktu baca artikel orisinal (P1)

Artikel orisinal memakai readMinutes dari data-artikel.json (hitung
kata/200). Berita tetap memakai nilai pipeline sampai cron diperbaiki
(butir 6.2).

## 5. Batch awal: 3 Edukasi + 3 Hobi

Ditulis ke data-artikel.json (lihat butir 3.1). Judul dan slug:

Edukasi:
1. Cara Membaca Berita Biar Tidak Gampang Kena Hoaks
   (cara-membaca-berita-biar-tidak-kena-hoaks)
2. Kenapa Pelajaran Baru Cepat Lupa, dan Cara Mengingatnya
   (kenapa-pelajaran-baru-cepat-lupa-dan-cara-mengingatnya)
3. Belajar Bahasa Inggris dari Nol Tanpa Kursus
   (belajar-bahasa-inggris-dari-nol-tanpa-kursus)

Hobi:
1. Merawat Tanaman Hias di Dalam Rumah Biar Tidak Gampang Mati
   (merawat-tanaman-hias-di-dalam-rumah)
2. Mulai Fotografi dengan HP: Lima Latihan untuk Melatih Mata
   (mulai-fotografi-dengan-hp)
3. Memancing di Sungai untuk Pemula: Persiapan Dasar sebelum Berangkat
   (memancing-di-sungai-untuk-pemula)

Masing-masing 400-600 kata, orisinal, tanpa parafrase berita, tanpa
angka/kutipan karangan, suara manusia sesuai butir 3.4.

## 6. Yang mengalir lewat push JSON vs yang butuh ZIP deploy

### 6.1 Mengalir lewat push JSON (tanpa deploy, agen utama yang push)

- data-artikel.json: tambah artikel harian, ubah, atau tambah kategori
  baru (bila suatu hari rubrik ketiga dibuka).
- data-redaksi.json: ubah info redaksi/byline default.
- data-berita.json, data-trending.json, data-arsip.json, koleksi-berita.json,
  pool-gambar.json: tetap seperti sekarang (cron carousel).
- Verifikasi tiap push: raw URL mengembalikan JSON valid + artikel baru
  tampil di situs (cek seksi Edukasi/Hobi).

### 6.2 Butuh ZIP deploy oleh Muhammad (sekali, untuk butir 4)

Semua edit butir 4 (index.html + sitemap.xml + robots.txt) masuk ZIP
deploy berikutnya. JANGAN buat ZIP sebelum Muhammad menyuruh (aturan
tetap). Setelah ZIP deploy, verifikasi live: footer menampilkan 4 tautan
kebijakan; halaman /privasi/, /kontak/, /tentang/, /syarat-ketentuan/
terbuka; seksi Politik hanya satu; kartu tidak lagi bertahun ganda;
artikel orisinal tampil di Edukasi/Hobi.

### 6.3 Tambahan untuk isi cron carousel (untuk agen utama, BUKAN diubah di sini)

Isi cron TIDAK diubah dalam tugas ini. Tiga tambahan yang diusulkan
untuk agen utama saat revisi cron berikutnya:

1. Headline di data-berita.json ikut membawa source + sourceUrl dari
   berita yang sama (satu baris di langkah 7c(a)).
2. read dihitung dari panjang teks isi (kata/200, minimal 1 menit),
   bukan "3 mnt baca" untuk semua.
3. Saat menyisipkan item segar ke kategori, ganti item yang sudah
   lebih dari 7 hari (bukan hanya memangkas bila melebihi 8), supaya
   ekor basi seperti siklon/crane 14 Nov di Entertainment tidak
   bertahan berminggu-minggu.

## 7. Keputusan terbuka (butuh Muhammad)

### 7.1 Model byline penulis

Pilihan: (a) tetap kolektif "Redaksi NusaTrance" untuk semua artikel;
(b) nama penulis per artikel (mis. penulis tetap atau kontributor);
(c) gabungan: artikel orisinal memakai nama penulis, berita memakai
"Redaksi NusaTrance". Mekanisme sudah mendukung ketiganya (field
author per artikel). Default saat ini: (a).

### 7.2 Nama pendiri di halaman Tentang + data-redaksi.json

DRAF (belum tampil di halaman live): "NusaTrance didirikan oleh
Muhammad Shihab di Banjarmasin, Kalimantan Selatan. Ia bertindak
sebagai pendiri dan penanggung jawab redaksi." Butuh OK Muhammad
sebelum draf ini masuk ke tentang/index.html dan data-redaksi.json.
Sampai disetujui, halaman Tentang tetap memakai kalimat lamanya
("dikelola oleh Redaksi NusaTrance").

### 7.3 Email kontak

Halaman Kontak sudah memakai farmatrance@gmail.com. Konfirmasi apakah
email ini tetap yang dipakai untuk redaksi/iklan/kerja sama, atau ada
email lain yang diinginkan.

### 7.4 Wording dialog "Segera hadir" (Store/Marketplace)

Draf: "Toko NusaTrance masih disiapkan. Kami kabari begitu sudah bisa
dibuka." Bila Muhammad mau wording lain, atau mau tombolnya dihapus
saja dari header/nav, itu keputusannya.

### 7.5 Sinkronisasi Space

Situs juga hidup sebagai Space nusatrance-homepage-berita-ala-infopulse
(ruang edit). Perubahan butir 4 dibuat di berkas export build-v88.
Perlu diputuskan: apakah Space ikut diperbarui dengan perubahan yang
sama (lewat artifact edit), atau export v88 menjadi sumber deploy
berikutnya dan Space disusul belakangan.

## 8. Kadensi harian seminggu (21-28 Nov 2026)

Target: tiap hari 2 artikel baru (1 Edukasi + 1 Hobi), 7 hari = 14
artikel. Batch awal 6 artikel menutup hari ke-1 sampai ke-3.

Alur harian (tanpa deploy):

1. Pagi: tulis 2 artikel (Edukasi + Hobi) mengikuti butir 3.4, 400-600
   kata, fakta terverifikasi, tanpa karangan.
2. Hitung kata + readMinutes, validasi JSON (python json.load).
3. Tambah ke data-artikel.json (artikel terbaru di urutan pertama
   tiap kategori), perbarui field updated.
4. Agen utama push ke GitHub (repo nusatrance-data).
5. Verifikasi: raw URL data-artikel.json menampilkan artikel baru;
   situs live menampilkan di seksi Edukasi/Hobi.
6. Catat judul + slug di laporan harian (chat), tanpa laporan
   konsolidasi terpisah.

Topik cadangan bila kehabisan ide (tetap orisinal, bukan berita):
Edukasi: cara membuat catatan yang gampang diingat; beda fakta dan
opini di media sosial; belajar berhitung cepat untuk belanja harian;
cara menulis email lamaran yang jelas. Hobi: merawat sepeda biar awet;
memasak dengan bahan sisa kulkas; berkebun sayur di pekarangan sempit;
membuat rak buku dari kardus bekas.

## 9. Ceklis penyerahan

- [ ] RENCANA-KONTEN-ORISINAL.md (berkas ini)
- [ ] data-artikel.json — 6 artikel, JSON valid, 400-600 kata/artikel
- [ ] data-redaksi.json — info redaksi (pendiri = DRAF)
- [ ] index.html (build-v88) — edit butir 4.1-4.10, diverifikasi lokal
- [ ] sitemap.xml + robots.txt — domain www.nusatrance.web.id
- [ ] Verifikasi lokal: serve folder build + curl halaman/JSON + node
      --check pada JS hasil ekstrak + grep bukti tiap perbaikan
- [ ] TIDAK dilakukan di sini: git push (agen utama), deploy Cloudflare
      (Muhammad dari ZIP), klik Resubmit AdSense, edit isi cron,
      kaitkan dengan emshihab, sentuh deploy-v3 RacunDecor / pilot TKA /
      isi foto produk.
