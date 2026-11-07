<template>
  <div 
    class="fixed bottom-0 right-0 left-16 z-20 transition-all duration-300 ease-in-out flex flex-col bg-white border-t border-slate-200 shadow-2xl rounded-t-3xl"
    :class="store.isBottomDrawerOpen ? 'h-[440px]' : 'h-16'"
  >
    <!-- Drawer Drag / Toggle Handle Bar -->
    <div 
      @click="store.isBottomDrawerOpen = !store.isBottomDrawerOpen"
      class="h-16 px-6 bg-slate-900 text-white rounded-t-3xl flex items-center justify-between cursor-pointer select-none hover:bg-slate-800 transition-colors"
    >
      <div class="flex items-center space-x-4">
        <!-- Drawer Chevron Indicator -->
        <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-300">
          <svg 
            class="w-5 h-5 transform transition-transform" 
            :class="store.isBottomDrawerOpen ? 'rotate-180' : 'rotate-0'"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
        </div>

        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400 block">Panel Masukan Data & Kontrol</span>
          <span class="text-sm font-extrabold text-white">
            {{ store.isBottomDrawerOpen ? 'Klik untuk Menyembunyikan' : 'Klik untuk Mengangkat & Memasukkan Data' }}
          </span>
        </div>
      </div>

      <!-- Quick Metrics Pills -->
      <div class="flex items-center space-x-3 text-xs" @click.stop>
        <div class="hidden sm:flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
          <span class="text-slate-400">Paket:</span>
          <span class="font-bold text-white font-mono">{{ store.packages.length }}/50</span>
        </div>

        <div class="hidden sm:flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
          <span class="text-slate-400">Kurir:</span>
          <span class="font-bold text-white font-mono">{{ store.couriers.length }}/10</span>
        </div>

        <div v-if="store.isRouteStarted" class="flex items-center space-x-2 bg-red-950/80 px-3 py-1.5 rounded-xl border border-red-800 text-red-200">
          <span>Ditempuh:</span>
          <span class="font-bold font-mono text-white">{{ store.totalDistanceTraveledKm }} km</span>
          <span class="text-slate-400">/ {{ store.totalDistancePlannedKm }} km</span>
        </div>

        <!-- Action: Hitung Rute -->
        <button 
          v-if="store.canCalculate && !store.isRouteStarted"
          @click="store.calculateRoutes()"
          :disabled="!store.canCalculate"
          class="bg-red-600 hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-extrabold px-5 py-2 rounded-xl text-xs shadow-lg transition-all flex items-center space-x-2"
        >
          <span>{{ store.isCalculating ? 'Menghitung...' : 'Mulai Simulasi' }}</span>
          <span v-if="!store.isCalculating">🚀</span>
        </button>

        <!-- Action: Step Execution (Lanjut) -->
        <div v-else-if="store.isRouteStarted" class="flex items-center space-x-2">
          <!-- Advance Specific Courier or All -->
          <button 
            @click="store.advanceAllCouriers()"
            :disabled="!store.canAdvanceAny || store.isCalculating"
            class="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-extrabold px-4 py-2 rounded-xl text-xs shadow-md transition-all flex items-center space-x-1"
            title="Lanjut 1 langkah untuk semua kurir aktif"
          >
            <span>Lanjut Semua</span>
            <span>⏩</span>
          </button>

          <!-- Dropdown Courier Steps -->
          <div class="relative group">
            <button class="bg-slate-700 hover:bg-slate-600 text-white font-bold px-3 py-2 rounded-xl text-xs">
              Lanjut Kurir ▾
            </button>
            <div class="absolute bottom-full right-0 mb-2 w-48 bg-white text-slate-800 rounded-xl shadow-2xl border border-slate-200 p-2 hidden group-hover:block z-50">
              <div v-for="c in store.couriers" :key="c.id" class="p-1.5 flex items-center justify-between hover:bg-slate-50 rounded-lg">
                <span class="text-xs font-bold" :style="{ color: c.color }">{{ c.name }}</span>
                <button 
                  @click="store.advanceCourierStep(c.id)"
                  :disabled="!store.courierStates[c.id] || store.courierStates[c.id].isFinished"
                  class="bg-slate-900 disabled:opacity-30 text-white text-[10px] px-2 py-1 rounded font-bold"
                >
                  {{ store.courierStates[c.id]?.isFinished ? 'Selesai' : 'Lanjut' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Action: Reset -->
        <button 
          @click="store.resetSession()"
          :disabled="store.isCalculating"
          class="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-bold px-3 py-2 rounded-xl text-xs border border-slate-700 transition-all"
          title="Reset Sesi"
        >
          Reset
        </button>
      </div>
    </div>

    <div v-show="store.isBottomDrawerOpen" class="flex-1 flex flex-col overflow-hidden bg-slate-50">
      <!-- Tabs Navigation -->
      <div class="flex border-b border-slate-200 bg-white px-6">
        <button 
          @click="store.bottomDrawerTab = 'packages'; store.clickMode = 'package'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'packages' ? 'border-red-600 text-red-600 bg-red-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Input Paket & Skenario</span>
          <span class="px-1.5 py-0.5 bg-slate-100 rounded text-[10px] text-slate-600 font-mono">{{ store.packages.length }}/50</span>
        </button>

        <button 
          @click="store.bottomDrawerTab = 'couriers'; store.clickMode = 'ref_point'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'couriers' ? 'border-red-600 text-red-600 bg-red-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Kelola Kurir & Titik Acuan</span>
          <span class="px-1.5 py-0.5 bg-slate-100 rounded text-[10px] text-slate-600 font-mono">{{ store.couriers.length }}/10</span>
        </button>

        <button 
          @click="store.bottomDrawerTab = 'params'; store.clickMode = 'package'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'params' ? 'border-red-600 text-red-600 bg-red-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Parameter Model</span>
        </button>

        <button 
          @click="store.bottomDrawerTab = 'history'; store.clickMode = 'package'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'history' ? 'border-red-600 text-red-600 bg-red-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Riwayat Rute</span>
          <span v-if="store.stepHistory.length > 0" class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[10px] font-mono">
            {{ store.stepHistory.length }}
          </span>
        </button>
      </div>

      <!-- Tab Contents Area -->
      <div class="flex-1 overflow-y-auto p-6">
        
        <!-- =================== TAB 1: PACKAGES & SCENARIOS =================== -->
        <div v-if="store.bottomDrawerTab === 'packages'" class="space-y-4">
          <!-- Top Tool Bar: Presets & Mode Selector -->
          <div class="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200">
            <!-- Mode Toggle -->
            <div class="flex items-center space-x-2">
              <span class="text-xs font-bold text-slate-700">Mode Klik Peta:</span>
              <button
                @click="store.clickMode = 'package'"
                :disabled="!store.canStartPackageInput"
                class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all"
                :class="store.clickMode === 'package' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
              >
                📦 Tambah Paket
              </button>
              <span v-if="!store.canStartPackageInput" class="text-xs text-amber-700">
                Tambahkan kurir dan titik acuan melalui tab
                <button class="font-bold underline" @click="store.bottomDrawerTab = 'couriers'; store.clickMode = 'ref_point'">Kelola Kurir</button>.
              </span>
            </div>

            <!-- Scenario Preset Loader (FR-18) -->
            <div class="flex items-center space-x-2">
              <span class="text-xs font-bold text-slate-700">Muat Skenario Uji:</span>
              <button 
                v-for="sc in store.scenarios" 
                :key="sc.id"
                @click="store.loadScenario(sc.id)"
                :disabled="!store.canStartPackageInput || store.isRouteStarted || store.isCalculating"
                class="px-2.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-40 transition-all border border-slate-200"
                :title="sc.description"
              >
                {{ sc.id.replace('scenario-', '') }} Paket
              </button>
              <button 
                @click="store.packages = []; store.resetRoutingStateOnly()"
                :disabled="store.isRouteStarted || store.isCalculating || store.packages.length === 0"
                class="px-2.5 py-1.5 rounded-xl text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 transition-all"
              >
                Kosongkan Paket
              </button>
            </div>
          </div>

          <!-- Package List Table -->
          <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div class="p-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-xs">
              <span class="font-bold text-slate-700">Daftar Titik Paket J&T (Total: {{ store.packages.length }})</span>
              <span class="text-slate-500 font-medium">Batas teknis: Maksimal 50 paket</span>
            </div>

            <div v-if="store.packages.length === 0" class="py-8 text-center text-xs text-slate-400">
              <template v-if="store.canStartPackageInput">Belum ada paket. Klik di peta atau pilih skenario uji di atas.</template>
              <template v-else>Input paket terkunci sampai kurir dan titik acuan siap.</template>
            </div>

            <div v-else class="max-h-56 overflow-y-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 text-slate-600 font-bold sticky top-0 border-b border-slate-200">
                  <tr>
                    <th class="p-2.5">ID</th>
                    <th class="p-2.5">Nama Lokasi</th>
                    <th class="p-2.5">Latitude</th>
                    <th class="p-2.5">Longitude</th>
                    <th class="p-2.5">Kurir Terpilih</th>
                    <th class="p-2.5">Urutan ACO</th>
                    <th class="p-2.5 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="(pkg, idx) in store.packages" :key="pkg.id" class="hover:bg-slate-50">
                    <td class="p-2.5 font-bold text-slate-700 font-mono">{{ pkg.id }}</td>
                    <td class="p-2.5 font-medium text-slate-800">{{ pkg.name || `Titik #${idx + 1}` }}</td>
                    <td class="p-2.5 font-mono text-slate-500">{{ pkg.lat }}</td>
                    <td class="p-2.5 font-mono text-slate-500">{{ pkg.lng }}</td>
                    <td class="p-2.5 font-semibold">
                      <span 
                        v-if="pkg.courier_id"
                        class="px-2 py-0.5 rounded-full text-[10px] text-white font-bold"
                        :style="{ background: getCourierColor(pkg.courier_id) }"
                      >
                        {{ getCourierName(pkg.courier_id) }}
                      </span>
                      <span v-else class="text-slate-400 text-[11px]">-</span>
                    </td>
                    <td class="p-2.5 font-mono font-bold text-blue-600">
                      {{ pkg.order ? `#${pkg.order}` : '-' }}
                    </td>
                    <td class="p-2.5 text-right">
                      <button 
                        @click="store.removePackage(pkg.id)"
                        :disabled="store.isRouteStarted || store.isCalculating"
                        class="text-red-500 hover:text-red-700 font-bold disabled:opacity-30"
                        title="Hapus Titik"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- =================== TAB 2: COURIERS =================== -->
        <div v-else-if="store.bottomDrawerTab === 'couriers'" class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs text-slate-500">Tambahkan kurir, pilih kurir, lalu klik peta untuk membuat titik acuan. Maksimal 10 kurir.</span>
            <button 
              @click="store.addCourier()"
              :disabled="store.couriers.length >= 10 || store.isRouteStarted || store.isCalculating"
              class="bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white font-bold text-xs px-3.5 py-2 rounded-xl transition-all shadow"
            >
              + Tambah Kurir Baru
            </button>
          </div>

          <div v-if="store.couriers.length === 0" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-800">
            Belum ada kurir. Tambahkan kurir, pilih kurir tersebut, lalu klik peta untuk menetapkan titik acuannya.
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div 
              v-for="c in store.couriers" 
              :key="c.id"
              class="bg-white border rounded-2xl p-4 shadow-sm transition-all"
              :class="store.activeCourierId === c.id ? 'border-red-500 ring-2 ring-red-100' : 'border-slate-200'"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <input 
                    type="color" 
                    v-model="c.color" 
                    :disabled="store.isRouteStarted || store.isCalculating"
                    class="w-6 h-6 rounded border-0 cursor-pointer" 
                  />
                  <input 
                    type="text" 
                    v-model="c.name" 
                    :disabled="store.isRouteStarted || store.isCalculating"
                    class="text-xs font-bold text-slate-800 border-b border-transparent focus:border-slate-300 outline-none px-1"
                  />
                </div>

                <button 
                  v-if="store.couriers.length > 1 && !store.isRouteStarted"
                  @click="store.removeCourier(c.id)"
                  class="text-red-400 hover:text-red-600 text-xs font-bold"
                  title="Hapus Kurir"
                >
                  ✕
                </button>
              </div>

              <!-- Ref Points Info -->
              <div class="bg-slate-50 rounded-xl p-2.5 text-xs space-y-1.5 border border-slate-100">
                <div class="flex justify-between text-slate-600 font-semibold">
                  <span>Titik Acuan (KNN Data Latih):</span>
                  <span class="font-bold font-mono">{{ c.ref_points.length }} titik</span>
                </div>
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="rp in c.ref_points" 
                    :key="rp.id"
                    class="px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] text-slate-700 flex items-center space-x-1"
                  >
                    <span>🎯 {{ rp.name }}</span>
                    <button 
                      v-if="!store.isRouteStarted"
                      @click="store.removeRefPoint(c.id, rp.id)"
                      class="text-red-500 font-bold ml-1 hover:text-red-700"
                    >
                      ×
                    </button>
                  </span>
                </div>
              </div>

              <!-- Set Active Button -->
              <button 
                @click="store.activeCourierId = c.id; store.clickMode = 'ref_point'"
                :disabled="store.isRouteStarted || store.isCalculating"
                class="mt-3 w-full py-1.5 rounded-xl text-xs font-bold transition-all border"
                :class="store.activeCourierId === c.id 
                  ? 'bg-amber-500 text-white border-amber-600 shadow' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'"
              >
                {{ store.activeCourierId === c.id ? 'Sedang Dipilih (Klik Peta untuk Acuan)' : 'Pilih Kurir untuk Set Acuan' }}
              </button>
            </div>
          </div>
        </div>

        <!-- =================== TAB 3: PARAMETERS =================== -->
        <div v-else-if="store.bottomDrawerTab === 'params'" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- KNN Parameters -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
              <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                <span>Parameter K-Nearest Neighbors (KNN)</span>
              </h4>

              <div>
                <div class="flex justify-between text-xs font-bold text-slate-700 mb-1">
                  <span>Nilai k (Jumlah Tetangga):</span>
                  <span class="font-mono text-indigo-600 font-black text-sm">{{ store.knnParams.k }}</span>
                </div>
                <input 
                  type="range" 
                  min="1" 
                  max="15" 
                  v-model.number="store.knnParams.k"
                  :disabled="store.isRouteStarted"
                  class="w-full accent-indigo-600 cursor-pointer"
                />
                <p class="text-[11px] text-slate-400 mt-1">Nilai bawaan: 3. Jika k melebihi jumlah titik acuan, k disesuaikan otomatis.</p>
              </div>

              <!-- Balance Load Toggle (FR-16) -->
              <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div>
                  <span class="text-xs font-bold text-slate-800 block">Opsi Seimbangkan Beban (FR-16)</span>
                  <span class="text-[11px] text-slate-500">Membatasi kapasitas kurir maksimal ceil(N / M).</span>
                </div>
                <input 
                  type="checkbox" 
                  v-model="store.knnParams.balanceLoad"
                  :disabled="store.isRouteStarted"
                  class="w-5 h-5 accent-red-600 cursor-pointer rounded"
                />
              </div>
            </div>

            <!-- ACO Parameters -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
              <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                <span>Parameter Ant Colony Optimization (ACO)</span>
              </h4>

              <div class="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <label class="font-bold text-slate-700 block mb-1">Pengaruh Feromon (&alpha;):</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    v-model.number="store.acoParams.alpha"
                    :disabled="store.isRouteStarted"
                    class="w-full border border-slate-200 rounded-xl px-3 py-1.5 font-mono"
                  />
                </div>

                <div>
                  <label class="font-bold text-slate-700 block mb-1">Pengaruh Jarak (&beta;):</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    v-model.number="store.acoParams.beta"
                    :disabled="store.isRouteStarted"
                    class="w-full border border-slate-200 rounded-xl px-3 py-1.5 font-mono"
                  />
                </div>

                <div>
                  <label class="font-bold text-slate-700 block mb-1">Laju Penguapan (&rho;):</label>
                  <input 
                    type="number" 
                    step="0.05" 
                    min="0.01" 
                    max="0.99" 
                    v-model.number="store.acoParams.rho"
                    :disabled="store.isRouteStarted"
                    class="w-full border border-slate-200 rounded-xl px-3 py-1.5 font-mono"
                  />
                </div>

                <div>
                  <label class="font-bold text-slate-700 block mb-1">Konstanta Deposit (Q):</label>
                  <input 
                    type="number" 
                    step="10" 
                    v-model.number="store.acoParams.q"
                    :disabled="store.isRouteStarted"
                    class="w-full border border-slate-200 rounded-xl px-3 py-1.5 font-mono"
                  />
                </div>

                <div class="col-span-2">
                  <label class="font-bold text-slate-700 block mb-1">Iterasi Maksimal:</label>
                  <input 
                    type="number" 
                    step="10" 
                    min="10" 
                    max="500" 
                    v-model.number="store.acoParams.iterations"
                    :disabled="store.isRouteStarted"
                    class="w-full border border-slate-200 rounded-xl px-3 py-1.5 font-mono"
                  />
                </div>
              </div>

              <button 
                @click="resetParamsToDefault()"
                :disabled="store.isRouteStarted"
                class="text-xs text-indigo-600 font-bold hover:underline"
              >
                Kembalikan Nilai Bawaan (Default)
              </button>
            </div>
          </div>
        </div>

        <!-- =================== TAB 4: HISTORY =================== -->
        <div v-else-if="store.bottomDrawerTab === 'history'" class="space-y-4">
          <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div class="p-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-xs">
              <span class="font-bold text-slate-700">Riwayat Rute Perjalanan Kurir (FR-13)</span>
              <span class="text-slate-500 font-medium">Langkah yang sudah ditempuh secara kronologis</span>
            </div>

            <div v-if="store.stepHistory.length === 0" class="py-8 text-center text-xs text-slate-400">
              Belum ada langkah yang dijalankan. Tekan tombol <strong>Lanjut</strong> saat rute telah dihitung.
            </div>

            <div v-else class="max-h-56 overflow-y-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 text-slate-600 font-bold sticky top-0 border-b border-slate-200">
                  <tr>
                    <th class="p-2.5">Kurir</th>
                    <th class="p-2.5">Langkah</th>
                    <th class="p-2.5">Dari</th>
                    <th class="p-2.5">Ke</th>
                    <th class="p-2.5">Jarak (km)</th>
                    <th class="p-2.5">Kumulatif (km)</th>
                    <th class="p-2.5">Sisa Titik</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                  <tr v-for="(h, idx) in store.stepHistory" :key="idx" class="hover:bg-slate-50">
                    <td class="p-2.5 font-sans font-bold" :style="{ color: h.courierColor }">{{ h.courierName }}</td>
                    <td class="p-2.5 text-slate-500">Langkah #{{ h.stepIndex }}</td>
                    <td class="p-2.5 font-sans text-slate-600">{{ h.fromName }}</td>
                    <td class="p-2.5 font-sans font-semibold text-slate-900">{{ h.toName }}</td>
                    <td class="p-2.5 font-bold text-slate-800">{{ h.distanceKm }}</td>
                    <td class="p-2.5 text-emerald-600 font-bold">{{ h.cumulativeKm }}</td>
                    <td class="p-2.5 text-indigo-600 font-bold">{{ h.remainingCount }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

function getCourierName(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.name : courierId
}

function getCourierColor(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.color : '#3B82F6'
}

function resetParamsToDefault() {
  store.knnParams.k = 3
  store.knnParams.balanceLoad = false
  store.acoParams.alpha = 1.0
  store.acoParams.beta = 3.0
  store.acoParams.rho = 0.5
  store.acoParams.q = 100.0
  store.acoParams.iterations = 100
}
</script>
