# PRD - Aplikasi Validasi Data Kependudukan

## 1. Informasi Produk

### Nama Produk

Validasi Data Kependudukan

### Versi Awal

v1.0

### Platform

- Ubuntu Linux
- Windows
- Desktop Application

### Teknologi

- Python 3.12+
- CustomTkinter
- Pandas
- OpenPyXL
- SQLite (opsional)
- PyInstaller

---

# 2. Latar Belakang

Instansi pendidikan, sekolah, kampus, lembaga kursus, maupun organisasi sering menerima data peserta dalam format Excel atau CSV.

Masalah yang sering terjadi:

- NIK tidak valid
- Nomor KK tidak valid
- Duplikasi NIK
- Duplikasi KK
- Nama kosong
- Tempat lahir kosong
- Tanggal lahir tidak sesuai NIK
- Kesalahan input operator
- Format file tidak konsisten

Proses pemeriksaan masih dilakukan secara manual dan membutuhkan waktu lama.

Aplikasi ini dibuat untuk mempercepat proses validasi dan meningkatkan akurasi data.

---

# 3. Tujuan Produk

Menyediakan aplikasi desktop yang mampu:

- Membaca data kependudukan
- Memvalidasi data otomatis
- Menampilkan kesalahan data
- Memberikan skor kesesuaian
- Mengekspor hasil validasi

---

# 4. Pengguna

## Operator Sekolah

Mengelola data siswa.

## Operator Kampus

Mengelola data mahasiswa.

## Admin Lembaga

Mengelola data peserta pelatihan.

## Tim Pendataan

Mengelola data penduduk atau warga.

---

# 5. Format Data Masukan

## Excel

- XLSX
- XLS

## CSV

- UTF-8
- UTF-8 BOM
- Separator koma
- Separator titik koma

## LibreOffice

- ODS (Roadmap)

---

# 6. Struktur Data

Kolom wajib:

| Kolom         |
| ------------- |
| NAMA          |
| NIK           |
| NO. KK        |
| TEMPAT LAHIR  |
| TANGGAL LAHIR |

Kolom tambahan diperbolehkan.

---

# 7. Dashboard

Menampilkan:

- Total Data
- Data Valid
- Data Tidak Valid
- NIK Duplikat
- KK Duplikat
- Tanggal Tidak Cocok
- Persentase Validasi

---

# 8. Fitur Upload

## Upload Excel

Pengguna memilih file Excel.

## Upload CSV

Pengguna memilih file CSV.

## Drag and Drop

Roadmap.

---

# 9. Validasi Data

## Validasi NIK

Pemeriksaan:

- Harus 16 digit
- Harus numerik
- Tidak boleh kosong

## Validasi KK

Pemeriksaan:

- Harus 16 digit
- Harus numerik
- Tidak boleh kosong

## Validasi Nama

Pemeriksaan:

- Tidak boleh kosong

## Validasi Tempat Lahir

Pemeriksaan:

- Tidak boleh kosong

## Validasi Tanggal Lahir

Pemeriksaan:

- Format valid
- Dapat dibaca sistem

## Validasi Tanggal Lahir Berdasarkan NIK

Sistem mengambil:

- Tanggal
- Bulan
- Tahun

dari NIK lalu membandingkan dengan kolom tanggal lahir.

---

# 10. Duplikasi

## NIK Duplikat

Sistem mendeteksi NIK yang muncul lebih dari satu kali.

## KK Duplikat

Sistem mendeteksi KK yang muncul lebih dari satu kali.

---

# 11. Sistem Penilaian

## Skor Awal

100

## Pengurangan

NIK tidak valid = -30

KK tidak valid = -20

Tanggal tidak sesuai = -25

Nama kosong = -10

Tempat lahir kosong = -10

NIK duplikat = -15

KK duplikat = -10

## Hasil

0 - 69 = Bermasalah

70 - 89 = Perlu Verifikasi

90 - 100 = Valid

---

# 12. Tampilan Hasil

Kolom tambahan:

| Kolom              |
| ------------------ |
| STATUS             |
| SKOR               |
| TINGKAT_KESESUAIAN |

Contoh:

VALID

atau

NIK Tidak Valid | KK Duplikat

---

# 13. Pewarnaan

## Hijau

Skor >= 90

## Kuning

Skor 70 - 89

## Merah

Skor < 70

---

# 14. Pencarian

Pencarian berdasarkan:

- Nama
- NIK
- KK

Real-time.

---

# 15. Filter

Filter:

- Semua Data
- Valid
- Tidak Valid
- NIK Duplikat
- KK Duplikat

---

# 16. Export

## Export Excel

Menghasilkan:

NAMA
NIK
NO. KK
TEMPAT LAHIR
TANGGAL LAHIR
STATUS
SKOR
TINGKAT_KESESUAIAN

## Export CSV

Format CSV hasil validasi.

---

# 17. Keamanan

Aplikasi berjalan lokal.

Data tidak dikirim ke server.

Tidak menyimpan data tanpa izin pengguna.

---

# 18. Kinerja

Target:

10.000 data < 10 detik

50.000 data < 1 menit

100.000 data < 3 menit

---

# 19. Roadmap V2

- Deteksi wilayah NIK
- Validasi kode provinsi
- Validasi kabupaten
- Validasi kecamatan
- Database referensi wilayah Indonesia
- Riwayat validasi
- Login pengguna
- Multi-user
- Export PDF
- Dashboard grafik
- API Integrasi Laravel
- Build AppImage Ubuntu
- Build EXE Windows

---

# 20. Roadmap V3

- Integrasi Web Service Dukcapil (jika tersedia akses resmi)
- AI Data Cleansing
- Deteksi kesalahan penulisan nama
- Sinkronisasi Google Sheets
- REST API
- Cloud Sync
- Audit Log
- Role Management
