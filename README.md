# SwiftRoute by J&T — Sistem Alokasi Paket Multi-Kurir KNN & Optimasi Rute ACO

> **Alokasi cerdas. Rute optimal. Pengiriman kilat.**

**SwiftRoute by J&T** adalah sistem pendukung keputusan logistik berbasis web untuk J&T Express Samarinda yang mengotomatiskan alokasi paket ke kurir terdekat dengan algoritma **K-Nearest Neighbors (KNN)**, lalu menyusun urutan kunjungan optimal menggunakan **Ant Colony Optimization (ACO)** pada jaringan jalan sesungguhnya (OSRM) — mempersingkat waktu, menghemat bahan bakar, dan meningkatkan efisiensi kurir.

---

## 🚀 Cara Menjalankan Aplikasi

Pastikan Python 3.10+ telah terpasang di komputer Anda.

### 0. Instal Dependensi Python
```bash
python -m pip install -r requirements.txt
```

### 1. Jalankan Langsung (Mode Terpadu)
```bash
python run.py
```
Akses antarmuka web di browser Anda: **[http://localhost:8001](http://localhost:8001)**
Dokumentasi interaktif OpenAPI / Swagger: **[http://localhost:8001/docs](http://localhost:8001/docs)**

### 2. Menjalankan Pengujian Otomatis (Unit & Integration Tests)
```bash
python -m pytest backend/tests
```

### 3. Mode Pengembangan Frontend (Opsional - Vite Hot Reload)
Jika Anda ingin mengubah tampilan Vue secara dinamis dengan hot-reload:
```bash
# Terminal 1 (Backend)
python run.py

# Terminal 2 (Frontend)
cd frontend
npm run dev
```
Akses Vite di: **http://localhost:5173**

## ☁️ Deploy ke Vercel

Konfigurasi Vercel sudah disiapkan di `vercel.json`; frontend dibangun sebagai situs statis dan API berjalan sebagai Python Function.

**Catatan paket:** Vercel Hobby gratis hanya untuk penggunaan personal/non-komersial. Gunakan Hobby untuk demo personal/akademik; jika aplikasi dipakai untuk operasional atau kepentingan bisnis J&T, gunakan paket berbayar yang sesuai dengan [ketentuan Vercel](https://vercel.com/legal/terms#4-hobby-plan).

1. Push repository ini ke GitHub.
2. Di [vercel.com/new](https://vercel.com/new), impor repository tersebut.
3. Pastikan **Root Directory** adalah root repository (`./`), bukan `frontend`.
4. Pilih paket Vercel yang sesuai dengan tujuan penggunaan dan deploy. Build command dan output directory sudah diatur di `vercel.json`.
5. Setelah berhasil, buka URL deployment. Tes API melalui `/api/config` dan `/api/scenarios`.

Untuk deploy selanjutnya, push perubahan ke branch GitHub yang terhubung; Vercel akan membangun ulang otomatis. API menggunakan layanan OSRM publik untuk jarak jalan, jadi ketersediaan dan batas pemakaiannya mengikuti layanan tersebut.

---

## 🎨 Fitur Antarmuka & Sesuai Kebutuhan Spesifik

1. **Peta Interaktif Samarinda**:
   - Depot pusat J&T Express Samarinda (Juanda, `-0.4897, 117.1352`).
   - Penanda paket berkode warna sesuai kurir pemenang.
   - Penanda titik acuan (*reference points*) per kurir.
   - Garis rute GeoJSON jalan nyata (OSRM) dengan fallback otomatis ke Haversine jika OSRM sedang lambat/offline.
   - Posisi kurir real-time bergerak secara bertahap saat tombol **Lanjut** ditekan.

2. **Panel Kiri (Eksplorasi & Tahapan Algoritma)**:
   - Posisi di sebelah kiri layar.
   - Dapat **melebar ke kanan-tengah menutupi 50% layar** ketika dibuka (*expand*).
   - **Tahap 1 (KNN)**: Menggunakan scikit-learn dan jarak jalan kendaraan dari OSRM untuk mencari $k$ titik acuan terdekat, menampilkan perhitungan suara (*voting*), *tie-breaking* pembobotan $1/d$, serta log penyeimbangan beban (*load balancing*). Alokasi gagal jika OSRM tidak tersedia atau rute jalan tidak ditemukan.
   - **Tahap 2 (ACO)**: Menampilkan rumus probabilitas transisi $P_{ij}$ dan pembaruan feromon $\tau_{ij}$, kurva konvergensi jarak per iterasi, log *milestone* iterasi semut, serta urutan perhentian.
   - **Tahap 3 (Evaluasi Akademik)**: Membandingkan alokasi (KNN vs K-Means vs Acak) dan rute (ACO, Nearest Neighbor, Dijkstra greedy, dan Urutan Klik). Setiap metode routing memiliki tombol yang membuka tab peta terpisah, menghitung ulang evaluasi metode itu dari input aktif, lalu menggambar rute bertahap; kecepatan dapat diatur hingga 5x.

3. **Panel Bawah (Drawer Masukan Data)**:
   - Panel di bagian bawah yang **dapat diangkat (*lift/expand*)** untuk memasukkan data dan diminimalkan agar pandangan ke peta tetap luas (*clean*).
   - **Alur Input**: Saat aplikasi dibuka, tentukan 1–10 kurir lalu tambahkan minimal satu titik acuan untuk setiap kurir di peta. Setelah itu, klik peta atau pilih skenario paket; KNN langsung menetapkan kurir dan ACO menampilkan urutan serta rutenya.
   - **Kelola Kurir**: Atur jumlah kurir dan titik acuan sebelum input paket; warna dan nama kurir dapat disesuaikan.
   - **Parameter**: Atur $k$, saklar *Seimbangkan Beban*, parameter $\alpha, \beta, \rho, Q$, jumlah semut, dan iterasi.
   - **Riwayat Rute**: Tabel langkah per kurir yang bertambah tiap klik **Lanjut**.

---

## 📂 Struktur Proyek

```text
jnt-aco-knn/
├── backend/
│   ├── aco.py             # Algoritma Ant Colony Optimization (Open TSP) & baseline solvers
│   ├── knn.py             # Algoritma KNN & greedy load balancing
│   ├── osrm.py            # Integrasi OSRM Table & Route API + Fallback Haversine
│   ├── comparison.py      # Modul komparasi ilmiah & benchmark
│   ├── schemas.py         # Skema validasi Pydantic
│   ├── main.py            # API FastAPI & static web server
│   ├── data/
│   │   └── scenarios.json # Data simulasi 10, 20, 30, 50 titik Samarinda
│   └── tests/             # Unit tests & integrasi
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.vue                   # Peta Leaflet & render rute
│   │   │   ├── AlgorithmExplorationPanel.vue # Panel kiri expand 50% tahapan algoritma
│   │   │   └── DataDrawer.vue                # Panel bawah slide-up masukan data
│   │   ├── stores/appStore.js                # State management Pinia
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── run.py                 # File runner utama satu langkah
├── pytest.ini             # Konfigurasi pengujian
└── README.md
```
