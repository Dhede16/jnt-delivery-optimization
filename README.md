# Sistem Alokasi Paket Multi-Kurir Berbasis KNN dan Optimasi Rute ACO pada J&T Express Samarinda

Aplikasi web sistem pendukung keputusan logistik untuk mengalokasikan paket J&T Express Samarinda ke beberapa kurir dengan algoritma **K-Nearest Neighbors (KNN)**, kemudian menyusun urutan kunjungan optimal tiap kurir menggunakan **Ant Colony Optimization (ACO)** berbasis rute jalan sesungguhnya (Open TSP).

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
Akses antarmuka web di browser Anda: **[http://localhost:8000](http://localhost:8000)**  
Dokumentasi interaktif OpenAPI / Swagger: **[http://localhost:8000/docs](http://localhost:8000/docs)**

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
   - **Tahap 3 (Evaluasi Akademik)**: Membandingkan alokasi (KNN vs K-Means vs Acak) dan rute (ACO, Nearest Neighbor, Dijkstra greedy, dan Urutan Klik). Setiap baris routing memiliki tombol simulasi sendiri yang membuka tab peta khusus untuk metode tersebut; kecepatan dapat diatur hingga 5x.

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
