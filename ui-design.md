# Spesifikasi UI: Aplikasi Pembagian Paket Kurir (KNN) dan Optimasi Rute (ACO)

Dokumen ini adalah panduan tampilan (UI) untuk merombak frontend aplikasi agar lebih rapi, konsisten, dan terstruktur. Gaya visual mengikuti dashboard referensi: bersih, banyak ruang kosong, kartu membulat dengan bayangan lembut, dan dominasi warna biru. Panel memakai **efek kaca transparan (glassmorphism)** yang melayang di atas peta agar tampilan terasa modern.

Dokumen ini hanya mengatur **tampilan dan interaksi**. Logika algoritma, API, dan model data tidak berubah (lihat `new-design.md`).

Nilai warna, ukuran, dan jarak adalah **usulan** dan dapat disesuaikan saat implementasi.

---

## 1. Gambaran Umum

Antarmuka satu halaman (SPA) berbasis Vue 3 + Tailwind CSS dengan peta Leaflet sebagai pusat. Pengguna mengatur kurir, titik acuan, dan paket, menjalankan alokasi KNN dan optimasi ACO, lalu memantau simulasi serta membandingkan metode.

**Prinsip desain:**

| Prinsip | Penerapan |
|---|---|
| Peta sebagai fokus | Peta selalu menjadi area terbesar; panel lain melayang atau menempel di sisinya |
| Transparansi proses | Setiap hasil KNN dan ACO dapat dibuka rinciannya di panel kiri |
| Panel kaca transparan | Panel melayang di atas peta dengan latar buram tembus pandang; teks tetap terbaca |
| Satu warna per kurir | Warna kurir konsisten di titik acuan, paket, rute, kartu, dan grafik |
| Hierarki jelas | Judul, kontrol, dan data dibedakan lewat ukuran, berat font, dan warna |
| Status selalu terlihat | Loading, peringatan, kesalahan, dan cadangan Haversine ditampilkan eksplisit |

---

## 2. Struktur Layout

Seluruh aplikasi berada dalam satu kartu besar bersudut membulat di atas latar abu-biru muda, sama seperti dashboard referensi.

| Area | Posisi | Lebar / Tinggi (usulan) | Fungsi |
|---|---|---|---|
| Sidebar ikon | Kiri | ~56 px | Navigasi antar tampilan dan pengaturan |
| Panel eksplorasi algoritma | Kiri (setelah sidebar) | ~360 px, dapat diperlebar hingga 50% layar | Tab KNN, ACO, Evaluasi |
| Peta utama | Tengah | Sisa lebar | Depot, titik acuan, paket, rute, posisi kurir |
| Panel masukan dan kontrol | Bawah | ~240 px, dapat dilipat | Paket/skenario, kurir/titik acuan, parameter, riwayat, simulasi |

```
┌────┬────────────────┬───────────────────────────────────────┐
│ S  │ Eksplorasi     │  Peta Utama                           │
│ I  │ Algoritma      │  ┌──────────────┐  [lokasi][+][−]     │
│ D  │ [KNN][ACO]     │  │ Ringkasan    │                     │
│ E  │ [Evaluasi]     │  │ Status Sesi  │      ● Depot        │
│ B  │                │  └──────────────┘   ◆ Titik acuan     │
│ A  │ (konten tab)   │                     ● Paket (warna)   │
│ R  │                │   Legenda kurir     ➤ Posisi kurir    │
│    ├────────────────┴───────────────────────────────────────┤
│    │ Panel Masukan & Kontrol                                │
│    │ [Paket] [Kurir] [Parameter] [Riwayat]    ▶ Mulai ⟲ Reset│
└────┴────────────────────────────────────────────────────────┘
```

**Catatan layout dengan panel transparan:** peta menjadi latar layar penuh (*full-bleed*) di belakang seluruh antarmuka. Panel eksplorasi (kiri), panel masukan dan kontrol (bawah), kartu ringkasan, legenda, dan kontrol peta melayang di atas peta dengan margin 12 px dari tepi, sehingga peta terlihat menembus panel. Sidebar tetap menempel di tepi kiri.

**Perilaku responsif:**

| Lebar layar | Perilaku |
|---|---|
| ≥ 1280 px | Layout penuh seperti sketsa di atas |
| 768–1279 px | Sidebar menyempit menjadi ikon saja; panel kiri menjadi laci (*drawer*) yang dapat dibuka/tutup |
| < 768 px | Peta layar penuh; panel kiri dan bawah menjadi *bottom sheet* dengan tab |

---

## 3. Palet Warna

### 3.1 Warna Antarmuka

| Peran | Warna | Penggunaan |
|---|---|---|
| Primer (biru) | `#3366FF` | Sidebar, tombol utama, tab aktif, penanda cluster |
| Primer gelap | `#2B4FD8` | Hover/aktif pada elemen biru |
| Primer muda | `#E8EEFB` | Latar chip, tab non-aktif, baris terpilih |
| Aksen turkuois | `#00C9A7` | Status berhasil, indikator hemat jarak |
| Latar aplikasi | `#F5F7FB` | Latar utama |
| Permukaan | `#FFFFFF` | Kartu, panel, popup |
| Teks utama | `#2B3A67` | Judul dan isi |
| Teks sekunder | `#8A94A8` | Keterangan, placeholder, label kecil |
| Garis/border | `#E3E8F2` | Pemisah, border input |
| Peringatan | `#F5A524` | Pesan peringatan, cadangan Haversine |
| Kesalahan | `#E5484D` | Pesan kesalahan (mis. OSRM `503`) |
| Sukses | `#2FB67C` | Alokasi/optimasi selesai |

### 3.2 Warna Kurir (maksimal 10)

Setiap kurir mendapat satu warna tetap. Pastikan warna dapat dibedakan di atas peta dan tidak hanya mengandalkan warna (lihat bagian Aksesibilitas).

| Kurir | Warna |
|---|---|
| 1 | `#3366FF` |
| 2 | `#FF6B6B` |
| 3 | `#2FB67C` |
| 4 | `#F5A524` |
| 5 | `#9B5DE5` |
| 6 | `#00B8D9` |
| 7 | `#F15BB5` |
| 8 | `#8D6E63` |
| 9 | `#5C6BC0` |
| 10 | `#26A69A` |

### 3.3 Warna Peta

| Elemen | Warna |
|---|---|
| Depot | `#2B3A67` (ikon gedung, ukuran lebih besar) |
| Garis rute | Warna kurir, tebal 4 px, sudut membulat |
| Garis rute cadangan (Haversine) | Warna kurir, putus-putus |
| Rute yang sudah ditempuh | Warna kurir penuh |
| Rute yang belum ditempuh | Warna kurir, opasitas 40% |

---

## 4. Tipografi

Font sans-serif bersih: **Inter** (utama), cadangan `system-ui`.

| Elemen | Ukuran | Berat | Warna |
|---|---|---|---|
| Judul halaman | 20 px | Medium | Teks utama |
| Judul panel/tab | 15 px | Semibold | Teks utama |
| Judul grup | 12 px | Semibold | Teks utama |
| Isi / item daftar | 13 px | Regular | Teks utama |
| Label sekunder | 12 px | Regular | Teks sekunder |
| Angka metrik besar | 24 px | Semibold | Primer |
| Teks chip/badge | 12 px | Medium | Primer |
| Label sidebar | 10 px | Regular | Putih |
| Kode/rumus | 12 px | Mono | Teks utama |

Ukuran teks minimum 12 px agar tetap terbaca.

---

## 5. Komponen

### 5.1 Sidebar Ikon (Kiri)
- Latar biru primer, sudut kiri membulat mengikuti kartu aplikasi.
- Logo di bagian atas.
- Menu ikon dengan label kecil: **Peta, Algoritma, Evaluasi, Riwayat**; **Pengaturan** di bagian bawah.
- Item aktif memakai latar biru lebih terang dan ikon putih penuh.

### 5.2 Panel Eksplorasi Algoritma (Kiri)
- Kartu putih, radius 12 px, dengan tiga tab di atas: **KNN**, **ACO**, **Evaluasi**.
- Tab aktif: garis bawah biru + teks biru. Tab non-aktif: teks abu-abu.
- Tombol **perlebar** (ikon panah) untuk menggandakan lebar hingga 50% layar.
- Isi dapat di-*scroll* secara independen dari peta.

**Tab KNN**

| Bagian | Isi |
|---|---|
| Ringkasan | Nilai `k`, jumlah paket, jumlah titik acuan, status penyeimbangan beban |
| Kartu per paket | Nama paket, kurir pemenang (chip berwarna), daftar tetangga terpilih beserta jarak (m), suara, bobot `1/(jarak_km + 10⁻⁷)`, penanda seri |
| Catatan pemindahan | Daftar paket yang dipindahkan karena penyeimbangan beban |
| Peringatan | Banner kuning jika `k` diturunkan |

**Tab ACO**

| Bagian | Isi |
|---|---|
| Pemilih kurir | Dropdown/chip kurir untuk melihat hasil per kurir |
| Parameter | Ringkasan `α`, `β`, `ρ`, `Q`, iterasi, jumlah semut |
| Hasil | Urutan kunjungan, jarak (m), waktu eksekusi |
| Grafik konvergensi | Grafik garis jarak terbaik per iterasi |
| Log iterasi | Tabel yang dapat di-*scroll* |
| Pembanding | Jarak Nearest Neighbor dan urutan masukan |

**Tab Evaluasi**

| Bagian | Isi |
|---|---|
| Alokasi | Tabel KNN vs K-Means vs Acak (paket per kurir, jarak total, jarak maksimum, simpangan baku, waktu) |
| Rute | Tabel ACO vs Nearest Neighbor vs Dijkstra greedy vs urutan masukan (jarak total, waktu, penghematan) |
| Penonjolan | Nilai terbaik per kolom ditandai tebal dan hijau |
| Aksi | Tombol **Buka simulasi** pada baris rute, membuka tab peta baru |

### 5.3 Peta Utama
- Peta dasar OpenStreetMap, ditampilkan dengan nuansa lembut.
- **Depot:** ikon gedung besar berwarna navy dengan label.
- **Titik acuan:** penanda berbentuk belah ketupat (◆) berwarna kurir.
- **Paket:** lingkaran berwarna kurir hasil alokasi dengan nomor urutan kunjungan; sebelum alokasi berwarna abu-abu.
- **Posisi kurir (simulasi):** ikon panah/kurir berwarna kurir dengan halo transparan.
- **Rute:** garis berwarna kurir; panah arah kecil di sepanjang garis.
- **Popup paket:** nama, kurir, urutan, jarak dari titik sebelumnya.
- **Kontrol peta (kanan atas):** kartu putih vertikal berisi lokasi, zoom in (+), zoom out (−).
- **Legenda kurir (kiri bawah peta):** kartu kecil berisi warna, nama kurir, dan jumlah paket.
- **Kartu ringkasan sesi (kiri atas peta):** jumlah kurir, jumlah paket, total jarak.

### 5.4 Panel Masukan dan Kontrol (Bawah)
Kartu putih dengan tab di sisi kiri dan tombol aksi di sisi kanan.

| Tab | Isi |
|---|---|
| Paket / Skenario | Dropdown skenario bawaan, tombol **Muat**, daftar paket (nama, koordinat, hapus), indikator `n / 50`, instruksi "klik peta untuk menambah paket" |
| Kurir / Titik acuan | Kartu per kurir: warna, nama, daftar titik acuan, tombol tambah titik, hapus; indikator `n / 10`; peringatan jika kurir belum punya titik acuan |
| Parameter | Input `k`, sakelar penyeimbangan beban, `α`, `β`, `ρ`, `Q`, iterasi, jumlah semut, tombol **Atur ulang** ke bawaan |
| Riwayat | Daftar langkah simulasi dan peristiwa (paket diantar, kurir selesai) |

**Tombol aksi (kanan):**

| Tombol | Gaya | Fungsi |
|---|---|---|
| Mulai | Primer penuh | Menjalankan alokasi, optimasi, dan menyiapkan rute |
| Langkah kurir | Outline biru | Maju satu paket untuk satu kurir |
| Langkah semua | Outline biru | Maju satu paket untuk seluruh kurir |
| Reset | Outline abu-abu | Mengembalikan sesi ke awal |

### 5.5 Elemen Umum

| Komponen | Spesifikasi |
|---|---|
| Kartu / panel | Gaya kaca (lihat 6.2), radius 12 px, padding 12–16 px, bayangan lembut |
| Input & dropdown | Tinggi 36 px, radius 6 px, border `#E3E8F2`, ikon chevron di kanan |
| Chip kurir | Latar warna kurir 15%, teks warna kurir, radius 6 px, titik warna di kiri |
| Badge status | Radius penuh, ikon + teks (Selesai, Peringatan, Kesalahan) |
| Tombol primer | Latar `#3366FF`, teks putih, radius 6 px, tinggi 36 px |
| Tombol sekunder | Outline `#3366FF`, teks biru |
| Tabel | Header latar `#F5F7FB`, baris zebra halus, angka rata kanan |
| Banner pesan | Strip berwarna di atas konten dengan ikon, pesan, dan tombol tutup |

---

## 6. Spasi, Radius, Bayangan, dan Efek Transparan

### 6.1 Spasi, Radius, dan Bayangan

| Token | Nilai |
|---|---|
| Radius kartu aplikasi | 18 px |
| Radius kartu/panel | 12 px |
| Radius input/tombol/chip | 6 px |
| Padding kartu | 12–16 px |
| Jarak antar kartu | 12 px |
| Jarak antar item daftar | 8 px |
| Bayangan kartu biasa | `0 2px 8px rgba(30, 50, 100, 0.08)` |
| Bayangan panel melayang | `0 12px 30px rgba(51, 102, 255, 0.25)` |
| Bayangan popup peta | `0 6px 20px rgba(0, 0, 0, 0.12)` |

### 6.2 Efek Transparan (Glassmorphism)

Efek kaca dibuat dari tiga lapisan: latar putih semi-transparan, buram latar belakang (*backdrop blur*), dan border tipis terang. Peta di belakang panel terlihat samar sehingga antarmuka terasa ringan dan berlapis.

| Level | Dipakai pada | Latar | Blur | Border |
|---|---|---|---|---|
| Kaca standar | Panel eksplorasi, panel kontrol, kartu ringkasan, legenda | `rgba(255, 255, 255, 0.65)` | 16 px | `1px solid rgba(255, 255, 255, 0.6)` |
| Kaca padat | Tabel, log iterasi, area dengan banyak teks | `rgba(255, 255, 255, 0.85)` | 20 px | `1px solid rgba(255, 255, 255, 0.7)` |
| Kaca biru | Sidebar, tombol utama melayang | `rgba(51, 102, 255, 0.78)` | 12 px | `1px solid rgba(255, 255, 255, 0.25)` |
| Kaca popup | Popup peta, tooltip, dropdown | `rgba(255, 255, 255, 0.80)` | 12 px | `1px solid rgba(255, 255, 255, 0.7)` |

**Aturan penerapan:**

| Aturan | Penjelasan |
|---|---|
| Saturasi | Tambahkan `saturate(160%)` pada blur agar warna peta di belakang panel tidak pucat |
| Garis tepi atas | Tambahkan sorotan tipis `inset 0 1px 0 rgba(255, 255, 255, 0.8)` untuk kesan kaca |
| Teks | Gunakan warna teks utama `#2B3A67`; jangan taruh teks kecil di atas kaca berlatar sibuk, gunakan Kaca padat |
| Peta | Gunakan gaya peta terang agar kontras teks di atas kaca tetap aman |
| Kinerja | Batasi jumlah elemen berblur yang tampil bersamaan; jangan beri blur pada penanda peta; blur maksimum 20 px |
| Cadangan | Jika `backdrop-filter` tidak didukung, pakai latar hampir solid `rgba(255, 255, 255, 0.95)` |
| Transparansi dikurangi | Hormati `prefers-reduced-transparency` dan `prefers-contrast: more` dengan latar solid |
| Bayangan | Gunakan bayangan lembut agar panel terpisah dari peta: `0 8px 32px rgba(31, 50, 110, 0.15)` |

**Contoh CSS:**

```css
.glass {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 8px 32px rgba(31, 50, 110, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-radius: 12px;
}

.glass-dense { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px) saturate(160%); }
.glass-popup { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px) saturate(160%); }
.glass-blue  { background: rgba(51, 102, 255, 0.78); backdrop-filter: blur(12px); border-color: rgba(255, 255, 255, 0.25); color: #fff; }

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass, .glass-dense, .glass-popup { background: rgba(255, 255, 255, 0.95); }
}

@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass, .glass-dense, .glass-popup { background: #ffffff; backdrop-filter: none; }
  .glass-blue { background: #3366ff; backdrop-filter: none; }
}
```

**Padanan Tailwind:** `bg-white/65 backdrop-blur-lg backdrop-saturate-150 border border-white/60 shadow-glass rounded-card`.

---

## 7. Keadaan Antarmuka (State)

| Keadaan | Tampilan |
|---|---|
| Awal (kosong) | Peta hanya menampilkan depot; panel bawah menampilkan petunjuk langkah 1–3 |
| Siap dijalankan | Tombol **Mulai** aktif jika setiap kurir punya titik acuan dan ada paket |
| Tidak siap | Tombol **Mulai** non-aktif dengan tooltip alasan (mis. "Kurir 2 belum punya titik acuan") |
| Memuat | Skeleton pada panel kiri, spinner pada tombol, peta tetap dapat digeser |
| Berhasil | Badge hijau "Alokasi dan rute selesai"; paket berwarna sesuai kurir |
| Peringatan | Banner kuning (mis. `k` diturunkan, memakai Haversine) |
| Cadangan Haversine | Badge kuning "Jarak garis lurus" dan garis rute putus-putus |
| Kesalahan OSRM (`503`) | Banner merah: alokasi gagal karena layanan jarak jalan tidak tersedia, dengan tombol **Coba lagi** |
| Simulasi berjalan | Posisi kurir bergerak; baris riwayat bertambah |
| Simulasi selesai | Badge "Semua paket terantar", ringkasan jarak per kurir |

---

## 8. Interaksi dan Perilaku

| Elemen | Perilaku |
|---|---|
| Klik peta | Menambah paket (atau titik acuan jika mode titik acuan aktif) |
| Hover paket/titik | Popup ringan dan penyorotan di panel kiri |
| Klik paket pada peta | Membuka rinciannya di tab KNN dan menggulir ke kartunya |
| Klik kartu di panel | Peta berpindah dan menyorot penanda terkait |
| Tab panel kiri | Berpindah KNN, ACO, Evaluasi tanpa kehilangan posisi gulir |
| Tombol perlebar | Panel melebar/menyempit dengan animasi 200 ms |
| Panel bawah | Dapat dilipat agar peta lebih luas |
| Buka simulasi (Evaluasi) | Membuka tab baru; data sesi dibagikan lewat penyimpanan lokal peramban |
| Reset | Meminta konfirmasi sebelum menghapus hasil |

Animasi singkat dan halus (150–250 ms); hormati pengaturan *reduced motion* pengguna.

---

## 9. Aksesibilitas

- Kontras teks putih di atas `#3366FF` memenuhi WCAG AA; periksa ulang untuk warna kurir.
- Jangan mengandalkan warna saja untuk membedakan kurir: tambahkan **nomor/inisial kurir** pada penanda dan legenda, serta pola garis berbeda bila perlu.
- Pada panel transparan, kontras teks tetap minimal WCAG AA terhadap latar terburuk (peta berwarna gelap atau ramai); gunakan Kaca padat bila perlu dan sediakan latar solid untuk `prefers-reduced-transparency`.
- Semua ikon tombol memiliki `aria-label` dan *tooltip*.
- Seluruh kontrol dapat dioperasikan dengan keyboard; indikator fokus berwarna biru 2 px.
- Banner kesalahan dan peringatan memakai `role="alert"`.
- Ukuran teks minimum 12 px; area sentuh minimum 40 × 40 px pada layar sentuh.

---

## 10. Saran Implementasi

| Aspek | Saran |
|---|---|
| Framework | Vue 3 + Tailwind CSS (sudah dipakai) |
| Peta | Leaflet dengan `L.divIcon` untuk penanda khusus (depot, belah ketupat, bernomor) |
| Grafik | Chart.js atau ECharts untuk kurva konvergensi |
| Ikon | Lucide atau Phosphor (gaya outline tipis) |
| Komponen reusable | `AppSidebar`, `AlgorithmPanel`, `KnnTab`, `AcoTab`, `EvaluationTab`, `MapView`, `CourierLegend`, `ControlPanel`, `CourierCard`, `StatusBanner`, `MetricTable` |
| Penyimpanan token | Variabel CSS + konfigurasi Tailwind agar tema mudah diubah |

**Variabel CSS:**

```css
:root {
  --color-primary: #3366ff;
  --color-primary-dark: #2b4fd8;
  --color-primary-soft: #e8eefb;
  --color-accent: #00c9a7;
  --color-bg: #f5f7fb;
  --color-surface: #ffffff;
  --color-text: #2b3a67;
  --color-text-muted: #8a94a8;
  --color-border: #e3e8f2;
  --color-warning: #f5a524;
  --color-error: #e5484d;
  --color-success: #2fb67c;
  --radius-app: 18px;
  --radius-card: 12px;
  --radius-input: 6px;
  --shadow-card: 0 2px 8px rgba(30, 50, 100, 0.08);
  --shadow-floating: 0 12px 30px rgba(51, 102, 255, 0.25);
  --glass-bg: rgba(255, 255, 255, 0.65);
  --glass-bg-dense: rgba(255, 255, 255, 0.85);
  --glass-bg-blue: rgba(51, 102, 255, 0.78);
  --glass-border: rgba(255, 255, 255, 0.6);
  --glass-blur: 16px;
  --shadow-glass: 0 8px 32px rgba(31, 50, 110, 0.15);
}
```

**Konfigurasi Tailwind (`tailwind.config.js`):**

```js
export default {
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#3366FF', dark: '#2B4FD8', soft: '#E8EEFB' },
        accent: '#00C9A7',
        surface: '#FFFFFF',
        canvas: '#F5F7FB',
        ink: { DEFAULT: '#2B3A67', muted: '#8A94A8' },
        line: '#E3E8F2',
      },
      borderRadius: { app: '18px', card: '12px', input: '6px' },
      boxShadow: {
        card: '0 2px 8px rgba(30, 50, 100, 0.08)',
        floating: '0 12px 30px rgba(51, 102, 255, 0.25)',
        glass: '0 8px 32px rgba(31, 50, 110, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
};
```
