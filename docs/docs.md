# Panduan Penyusunan Laporan Proyek

Dokumen ini menjadi bahan awal laporan tugas kuliah untuk proyek **Sistem Alokasi Paket Multi-Kurir Berbasis KNN dan Optimasi Rute ACO pada J&T Express Samarinda**. Sesuaikan identitas, format, dan hasil pengujian dengan ketentuan kampus. Bagian bertanda **[isi]** harus dilengkapi berdasarkan pekerjaan dan pengujian Anda sendiri.

## Identitas Laporan

- **Judul:** Sistem Alokasi Paket Multi-Kurir Berbasis KNN dan Optimasi Rute ACO pada J&T Express Samarinda
- **Disusun oleh:** Dhede Febrian Purnawiranto 256151011
- **Program studi / kelas:** D3 Teknik Informatika 
- **Mata kuliah / dosen pengampu:** Machine Learning 
- **Institusi / tahun:** Politeknik Negeri Samarinda 2026

## Draf Abstrak

Pengiriman paket pada suatu wilayah memerlukan pembagian paket kepada kurir dan penentuan urutan kunjungan yang efisien. Proyek ini mengembangkan aplikasi web sistem pendukung keputusan untuk simulasi pengiriman paket di Samarinda. Algoritma **K-Nearest Neighbors (KNN)** digunakan untuk mengalokasikan paket kepada kurir berdasarkan jarak ke titik acuan kurir, sedangkan **Ant Colony Optimization (ACO)** digunakan untuk menentukan urutan kunjungan paket dari depot tanpa keharusan kembali ke depot (Open TSP). Jarak jalan diperoleh melalui layanan OSRM; pada perhitungan matriks rute, aplikasi menyediakan fallback Haversine ketika layanan atau rute jalan tidak tersedia. Aplikasi dibangun dengan FastAPI pada backend dan Vue pada frontend serta menampilkan peta interaktif, tahapan algoritma, dan perbandingan metode. Pengujian dilakukan pada [jumlah/jenis data] dengan membandingkan [metode yang diuji]. Hasil pengujian menunjukkan [isi hasil berdasarkan pengukuran]. Dengan demikian, [kesimpulan berdasarkan hasil].

**Kata kunci:** alokasi kurir, KNN, ACO, Open TSP, optimasi rute, Samarinda.

> Abstrak final sebaiknya ditulis setelah pengujian selesai. Ganti semua bagian dalam kurung siku dengan data aktual.

## BAB I — Pendahuluan

### 1.1 Latar Belakang

Operasional pengiriman paket menghadapi dua keputusan yang saling berkaitan: menentukan kurir yang menangani setiap paket dan menentukan urutan kunjungan paket oleh masing-masing kurir. Pembagian yang hanya mempertimbangkan kedekatan dapat menghasilkan beban kerja yang tidak merata, sementara urutan kunjungan yang tidak terencana dapat menambah total jarak perjalanan.

Proyek ini memodelkan proses tersebut melalui dua tahap. KNN menentukan kurir berdasarkan kedekatan paket terhadap titik-titik acuan kurir. Setelah paket dialokasikan, ACO mencari urutan kunjungan dengan jarak total yang rendah. Peta interaktif digunakan untuk membantu pengguna memasukkan titik, melihat hasil alokasi, dan mengeksplorasi hasil rute.

**Konteks dan data lapangan yang perlu ditambahkan:** [jelaskan sumber masalah, kondisi proses yang diamati, dan sumber data yang benar-benar digunakan].

### 1.2 Rumusan Masalah

1. Bagaimana mengalokasikan paket kepada beberapa kurir berdasarkan kedekatan geografis dan jarak jalan?
2. Bagaimana menentukan urutan kunjungan paket untuk setiap kurir agar jarak perjalanan berkurang?
3. Bagaimana menyajikan proses dan hasil alokasi serta optimasi melalui aplikasi web berbasis peta?
4. Bagaimana hasil KNN dan ACO dibandingkan dengan metode pembanding yang tersedia?

Sesuaikan atau hapus rumusan yang tidak menjadi sasaran penelitian Anda.

### 1.3 Tujuan

1. Membangun aplikasi web simulasi alokasi paket multi-kurir.
2. Menerapkan KNN untuk klasifikasi paket berdasarkan titik acuan kurir dan jarak.
3. Menerapkan ACO untuk optimasi urutan kunjungan paket sebagai Open TSP.
4. Mengevaluasi hasil menggunakan metrik dan metode pembanding yang ditetapkan.

### 1.4 Batasan Masalah

- Wilayah simulasi berpusat di Samarinda dengan depot contoh J&T Express Drop Point Juanda pada koordinat **(-0.4897, 117.1352)**.
- Backend membatasi masukan hingga **10 kurir** dan **50 paket**.
- Setiap kurir memerlukan setidaknya satu titik acuan untuk proses alokasi.
- Skenario bawaan merupakan data simulasi di `backend/data/scenarios.json`; jangan menyebutnya sebagai data operasional perusahaan kecuali sudah diverifikasi.
- OSRM menyediakan jarak dan geometri jalan melalui layanan daring. Pada proses alokasi KNN, kegagalan memperoleh jarak jalan dilaporkan sebagai layanan tidak tersedia; endpoint matriks rute dapat menggunakan Haversine sebagai fallback.
- Rute ACO adalah Open TSP: dimulai dari depot dan mengunjungi seluruh paket kurir, tanpa menghitung perjalanan kembali ke depot.
- Aplikasi ini merupakan prototipe simulasi, bukan sistem pelacakan operasional atau integrasi resmi J&T Express.
- [Tambahkan batasan terkait data, perangkat, atau waktu penelitian.]

### 1.5 Manfaat

- **Akademis:** menjadi contoh penerapan klasifikasi berbasis jarak dan optimasi metaheuristik pada permasalahan distribusi.
- **Pengguna:** membantu mengeksplorasi pembagian paket dan urutan kunjungan dalam skenario simulasi.
- **Pengembangan:** menyediakan dasar untuk evaluasi dengan data yang lebih representatif dan metode tambahan.

## BAB II — Landasan Teori

### 2.1 Sistem Pendukung Keputusan dan Distribusi Kurir

Sistem yang dibuat membantu pengguna memperoleh rekomendasi alokasi dan urutan kunjungan dari masukan depot, titik acuan kurir, paket, dan parameter algoritma. Hasilnya merupakan rekomendasi simulasi; keputusan operasional tetap memerlukan validasi terhadap kondisi nyata seperti waktu layanan, kapasitas kendaraan, lalu lintas, dan jam kerja.

### 2.2 K-Nearest Neighbors

KNN mengidentifikasi sebanyak \(k\) titik acuan terdekat terhadap suatu paket. Pada proyek ini, label setiap titik acuan adalah ID kurir pemilik titik tersebut. Klasifikasi memakai matriks jarak yang telah dihitung (`metric="precomputed"`), bukan jarak koordinat sebagai fitur langsung.

Langkah implementasi:

1. Gabungkan titik acuan dari seluruh kurir.
2. Hitung jarak jalan paket ke setiap titik acuan dan jarak antartitik acuan.
3. Ambil \(k\) titik acuan terdekat untuk setiap paket.
4. Pilih kurir berdasarkan suara mayoritas label kurir.
5. Jika jumlah suara seri, gunakan total bobot invers jarak:

\[
w_i = \frac{1}{d_i + \epsilon}
\]

Di sini \(d_i\) adalah jarak paket ke titik acuan dalam kilometer dan \(\epsilon\) mencegah pembagian dengan nol. Jika \(k\) lebih besar dari jumlah titik acuan, nilai efektif \(k\) disesuaikan dengan jumlah titik acuan.

**Penyeimbangan beban opsional:** target beban maksimum dihitung sebagai \(\lceil P/C \rceil\), dengan \(P\) jumlah paket dan \(C\) jumlah kurir. Jika suatu kurir melebihi target, algoritma mencoba memindahkan paket terjauh dari titik acuan pemenangnya kepada kurir yang lebih sedikit bebannya, dengan mempertimbangkan peringkat kedekatan. Oleh karena itu, hasil akhir dapat berbeda dari klasifikasi KNN awal.

### 2.3 Ant Colony Optimization

ACO meniru perilaku semut yang membangun jalur dan memperkuat jalur yang dinilai baik. Untuk memilih titik berikutnya \(j\) dari titik saat ini \(i\), implementasi menggunakan probabilitas proporsional:

\[
P_{ij} =
\frac{\tau_{ij}^{\alpha}\eta_{ij}^{\beta}}
{\sum_{u \in U}\tau_{iu}^{\alpha}\eta_{iu}^{\beta}},
\qquad
\eta_{ij} = \frac{1}{d_{ij}+\epsilon}
\]

Keterangan:

- \(\tau_{ij}\): intensitas feromon pada sisi \(i \rightarrow j\).
- \(\eta_{ij}\): visibilitas berdasarkan jarak.
- \(\alpha\): pengaruh feromon.
- \(\beta\): pengaruh jarak/heuristik.
- \(U\): paket yang belum dikunjungi.

Setelah setiap iterasi, feromon menguap dan semut menyetor feromon berdasarkan panjang rute. Implementasi memakai penguapan \(\tau \leftarrow (1-\rho)\tau\), setoran sebesar \(Q/L\) untuk setiap rute semut, serta penguatan tambahan untuk rute terbaik yang ditemukan. Nilai feromon dibatasi untuk mencegah nilai numerik ekstrem. Tur dimulai dari depot dan tidak menambahkan sisi perjalanan kembali ke depot.

### 2.4 Jarak Jalan dan Haversine

OSRM digunakan untuk memperoleh jarak jalan mengemudi dan geometri rute. Haversine menghitung jarak garis lurus pada permukaan bumi menggunakan koordinat lintang dan bujur. Jarak Haversine tidak sama dengan jarak perjalanan jalan.

Dalam aplikasi, endpoint matriks rute dapat beralih ke Haversine bila OSRM gagal atau tidak memiliki koneksi untuk pasangan titik tertentu. Catat sumber jarak yang digunakan pada setiap eksperimen karena hasil jalan nyata dan garis lurus tidak dapat dibandingkan tanpa penjelasan.

### 2.5 Metode Pembanding

Fitur evaluasi proyek menyediakan:

- **Alokasi:** KNN, K-Means, dan alokasi acak (seed acak ditetapkan dalam implementasi).
- **Routing:** ACO, Nearest Neighbor, Dijkstra greedy, dan urutan input/manual.

Dijkstra di sini digunakan berulang kali untuk memilih paket tersisa yang paling dekat menurut jarak jalur terpendek pada matriks. Ini bukan pencarian seluruh permutasi rute optimal. Nearest Neighbor juga bersifat greedy. Jelaskan perbedaan tugas metode-metode ini saat membahas hasil.

## BAB III — Metodologi dan Perancangan

### 3.1 Metode Pengembangan dan Alur Sistem

Alur simulasi:

1. Pengguna menetapkan jumlah kurir, identitas, dan titik acuan kurir.
2. Pengguna memasukkan paket melalui peta atau memilih skenario bawaan.
3. Backend memperoleh jarak paket dan titik acuan melalui OSRM.
4. KNN menetapkan kurir untuk setiap paket; penyeimbangan beban dapat diaktifkan.
5. Backend membentuk matriks jarak depot dan paket untuk rute.
6. ACO menyusun urutan paket per kurir dan menghitung jarak tur.
7. Frontend menampilkan hasil, tahapan algoritma, geometri pada peta, dan evaluasi metode.

### 3.2 Arsitektur dan Teknologi

| Lapisan | Teknologi / komponen | Peran |
|---|---|---|
| Frontend | Vue 3, Vite, Pinia, Leaflet | Antarmuka peta, state aplikasi, panel algoritma, dan drawer masukan |
| Backend | Python, FastAPI, Pydantic | API, validasi skema, penyediaan file frontend hasil build |
| Perhitungan | scikit-learn, NumPy | KNN dengan matriks jarak precomputed dan perhitungan numerik |
| Jarak / rute | OSRM, Haversine sebagai fallback tertentu | Jarak jalan, matriks jarak, dan geometri rute |
| Pengujian | pytest, FastAPI TestClient | Pengujian fungsi inti dan endpoint API |

Komponen backend utama: `backend/knn.py`, `backend/aco.py`, `backend/osrm.py`, `backend/comparison.py`, `backend/schemas.py`, dan `backend/main.py`. Komponen antarmuka utama: `frontend/src/App.vue`, `frontend/src/components/`, dan `frontend/src/stores/appStore.js`.

Diagram alur sistem tersedia pada [assets/alur-sistem-jnt.drawio.png](assets/alur-sistem-jnt.drawio.png). Tambahkan diagram tersebut ke bab perancangan dan beri nomor serta keterangan sesuai format kampus.

### 3.3 Data dan Skenario

File skenario menyediakan simulasi Samarinda dengan jumlah paket **10, 20, 30, dan 50**. Setiap skenario memuat koordinat paket, daftar kurir, dan titik acuan. Detail skenario yang dipakai dalam laporan:

| Skenario | Jumlah paket | Jumlah kurir | Sumber data | Catatan |
|---|---:|---:|---|---|
| [nama/id] | [isi] | [isi] | [simulasi/observasi/dll.] | [isi] |
| [nama/id] | [isi] | [isi] | [simulasi/observasi/dll.] | [isi] |

Jelaskan cara data dibuat atau diperoleh, rentang koordinat, cara menentukan titik acuan, dan apakah data telah dianonimkan. Jangan memasukkan alamat atau data pribadi pelanggan ke dalam laporan.

### 3.4 Parameter Eksperimen

Catat parameter berikut sebelum setiap eksperimen agar hasil dapat ditelusuri:

| Parameter | Nilai bawaan aplikasi | Nilai eksperimen |
|---|---:|---:|
| \(k\) KNN | 1 dari konfigurasi API | [isi; panel dapat mengubah nilai] |
| Penyeimbangan beban | Tidak aktif | [aktif/tidak aktif] |
| \(\alpha\) ACO | 1.0 | [isi] |
| \(\beta\) ACO | 3.0 | [isi] |
| \(\rho\) ACO | 0.5 | [isi] |
| \(Q\) ACO | 100.0 | [isi] |
| Jumlah semut | Otomatis, sekurang-kurangnya 5 atau jumlah paket | [isi/otomatis] |
| Iterasi | 100 | [isi] |
| Sumber jarak | OSRM atau fallback Haversine | [isi dan bukti status] |

Perhatikan: beberapa metode ACO menggunakan pengacakan dan implementasi tidak menetapkan seed NumPy. Untuk mengukur variasi, jalankan beberapa pengulangan dengan parameter dan data yang sama; laporkan jumlah pengulangan dan cara merangkum hasil.

### 3.5 API Utama

| Endpoint | Fungsi |
|---|---|
| `GET /api/config` | Informasi depot, batas input, dan parameter bawaan |
| `GET /api/scenarios` | Mengambil skenario simulasi bawaan |
| `POST /api/matrix` | Menghitung matriks jarak depot-paket |
| `POST /api/allocate` | Mengalokasikan paket menggunakan KNN |
| `POST /api/optimize` | Mengoptimalkan urutan kunjungan menggunakan ACO |
| `POST /api/geometry` | Mengambil geometri rute jalan atau fallback garis lurus |
| `POST /api/compare` | Membandingkan metode alokasi dan routing |

### 3.6 Metrik Evaluasi

Gunakan metrik yang sesuai dengan pertanyaan penelitian dan definisikan satuan serta cara hitungnya:

- Total jarak rute seluruh kurir (meter atau kilometer).
- Jarak rute maksimum seorang kurir.
- Jumlah paket per kurir dan simpangan baku jumlah paket.
- Waktu eksekusi algoritma.
- Selisih atau persentase perubahan jarak terhadap baseline.
- [Metrik tambahan yang memang diukur].

Rumus persentase pengurangan jarak terhadap baseline:

\[
\text{Pengurangan (\%)} =
\frac{D_{\text{baseline}} - D_{\text{metode}}}
{D_{\text{baseline}}} \times 100\%
\]

Nilai positif berarti jarak metode lebih pendek; nilai negatif berarti lebih panjang. Pastikan membandingkan data, alokasi, matriks jarak, dan definisi rute yang setara. API perbandingan saat ini membatasi beberapa nilai penghematan di bawah nol menjadi nol, sehingga gunakan jarak mentah untuk menghitung ulang jika ingin melaporkan kenaikan jarak secara akurat.

### 3.7 Cara Menjalankan dan Menguji

Persyaratan: Python 3.10 atau lebih baru. Jalankan dari direktori proyek:

```bash
python -m pip install -r requirements.txt
python run.py
```

Antarmuka tersedia di `http://localhost:8000` dan dokumentasi interaktif API di `http://localhost:8000/docs`. Untuk menguji otomatis:

```bash
python -m pytest backend/tests
```

Frontend mode pengembangan (opsional):

```bash
cd frontend
npm install
npm run dev
```

Catat versi perangkat lunak, sistem operasi, tanggal pengujian, status akses internet/OSRM, dan hasil aktual perintah pytest: **[isi hasil pengujian Anda]**.

## BAB IV — Hasil dan Pembahasan

Jangan isi bab ini hanya dari klaim algoritma. Jalankan aplikasi, catat keluaran, dan sertakan tangkapan layar atau ekspor hasil yang mendukung angka.

### 4.1 Lingkungan Pengujian

- Perangkat / prosesor / memori: [isi]
- Sistem operasi: [isi]
- Versi Python dan dependensi utama: [isi]
- Tanggal dan jumlah pengulangan: [isi]
- Status OSRM dan sumber jarak aktual: [isi]

### 4.2 Hasil Alokasi

| Skenario | Metode | Kurir A (paket) | Kurir B (paket) | Kurir C (paket) | Simpangan baku beban | Waktu (ms) |
|---|---|---:|---:|---:|---:|---:|
| [isi] | KNN | [isi] | [isi] | [isi] | [isi] | [isi] |
| [isi] | K-Means | [isi] | [isi] | [isi] | [isi] | [isi] |
| [isi] | Acak | [isi] | [isi] | [isi] | [isi] | [isi] |

Bahas apakah alokasi sesuai kedekatan geografis, dampak penyeimbangan beban, dan perubahan jarak total. Jumlah kolom kurir perlu disesuaikan dengan skenario.

### 4.3 Hasil Optimasi Rute

| Skenario / kurir | ACO (km) | Nearest Neighbor (km) | Dijkstra greedy (km) | Urutan input (km) | Pengurangan ACO vs baseline (%) |
|---|---:|---:|---:|---:|---:|
| [isi] | [isi] | [isi] | [isi] | [isi] | [hitung dari jarak mentah] |

Laporkan juga jumlah iterasi, jumlah semut, waktu eksekusi, dan bila memungkinkan variasi hasil antar-pengulangan. ACO bersifat stokastik; satu hasil terbaik tidak cukup untuk menyimpulkan kinerja rata-rata.

### 4.4 Pengujian Fungsional

Tes yang tersedia mencakup jarak Haversine, alokasi KNN, penyeimbangan beban, penggunaan matriks jarak jalan, kasus ACO, metode pembanding, dan respons endpoint ketika OSRM gagal. Lengkapi tabel dengan keluaran pengujian aktual:

| Pengujian | Hasil yang diharapkan | Hasil aktual | Status |
|---|---|---|---|
| `python -m pytest backend/tests` | Semua tes lulus | [isi] | [lulus/gagal] |
| Alokasi KNN melalui UI/API | Setiap paket memperoleh kurir | [isi] | [isi] |
| Optimasi ACO melalui UI/API | Seluruh paket kurir dikunjungi | [isi] | [isi] |
| Fallback / layanan OSRM | Pesan dan sumber jarak sesuai kondisi | [isi] | [isi] |

### 4.5 Pembahasan dan Ancaman Validitas

Pertimbangkan untuk membahas:

- Apakah titik acuan cukup mewakili wilayah kerja kurir.
- Perbedaan jarak jalan OSRM dan jarak garis lurus Haversine.
- Dampak keterbatasan layanan OSRM publik, jaringan, dan perubahan data peta.
- Pengaruh parameter KNN/ACO dan pengacakan ACO terhadap variasi hasil.
- Batas Open TSP yang tidak memasukkan perjalanan kembali ke depot.
- Faktor operasional yang belum dimodelkan: kemacetan, kapasitas, durasi layanan, prioritas paket, dan jam kerja.
- Karena data bawaan bersifat simulasi, hasilnya tidak langsung membuktikan peningkatan kinerja operasional perusahaan.

## BAB V — Kesimpulan dan Saran

### 5.1 Kesimpulan

Jawab rumusan masalah menggunakan temuan terukur:

1. [Kesimpulan penerapan alokasi KNN dan hasil pembagian paket.]
2. [Kesimpulan penerapan ACO dan hasil jarak dibanding baseline.]
3. [Kesimpulan fungsi aplikasi dan pengujian.]

Hindari menyatakan metode selalu lebih baik jika hasil pengujian tidak mendukungnya.

### 5.2 Saran

- Uji menggunakan data historis atau data lapangan yang tervalidasi dan dianonimkan.
- Ulangi ACO beberapa kali dan laporkan rerata serta variasi hasil.
- Tambahkan faktor operasional seperti kapasitas kendaraan, jam kerja, dan waktu pelayanan.
- Evaluasi kualitas titik acuan dan strategi penyeimbangan beban.
- Gunakan layanan routing yang sesuai untuk penggunaan operasional dan perhatikan batas pemakaian layanan.

## Lampiran yang Disarankan

- Diagram alur sistem: [assets/alur-sistem-jnt.drawio.png](assets/alur-sistem-jnt.drawio.png).
- Tabel data eksperimen dan parameter.
- Bukti hasil pengujian otomatis.
- Tangkapan layar peta, hasil alokasi, dan panel evaluasi.
- Contoh respons API yang telah dibersihkan dari informasi sensitif.
- Daftar pustaka dari sumber ilmiah yang benar-benar dibaca dan dikutip.

## Daftar Pustaka — Catatan

Tambahkan referensi akademik yang Anda telusuri sendiri untuk teori KNN, ACO, TSP, Haversine, dan OSRM. Gunakan format sitasi yang ditentukan kampus; jangan mengutip panduan ini atau kode proyek sebagai pengganti sumber teori primer.
