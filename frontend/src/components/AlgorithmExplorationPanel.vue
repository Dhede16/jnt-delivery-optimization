<template>
  <div 
    class="fixed top-0 left-0 bottom-0 z-30 transition-all duration-300 ease-in-out flex shadow-2xl"
    :class="store.isLeftPanelExpanded ? 'w-[50vw]' : 'w-16'"
  >
    <!-- Collapsed Slim Vertical Bar -->
    <div 
      class="w-16 h-full bg-slate-900 border-r border-slate-800 flex flex-col items-center py-5 justify-between text-white select-none z-20 shrink-0"
    >
      <div class="flex flex-col items-center space-y-6">
        <!-- Logo / Icon -->
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center font-black text-sm shadow-lg tracking-tighter">
          J&T
        </div>

        <!-- Toggle Expand Button -->
        <button 
          @click="store.isLeftPanelExpanded = !store.isLeftPanelExpanded"
          class="p-2.5 rounded-xl hover:bg-slate-800 text-slate-300 hover:text-white transition-all flex flex-col items-center"
          :title="store.isLeftPanelExpanded ? 'Kecilkan Panel' : 'Perlebar Tahapan Algoritma'"
        >
          <svg v-if="!store.isLeftPanelExpanded" class="w-6 h-6 transform rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
          <span class="text-[9px] mt-1 font-semibold text-slate-400">
            {{ store.isLeftPanelExpanded ? 'Tutup' : 'Buka' }}
          </span>
        </button>

        <div class="w-8 h-px bg-slate-800"></div>

        <!-- Quick Tab Nav Icons -->
        <button 
          @click="selectTab('knn')"
          class="p-2.5 rounded-xl transition-all flex flex-col items-center"
          :class="store.activeAlgoTab === 'knn' ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/50' : 'text-slate-400 hover:text-white'"
          title="Tahap 1: KNN Alokasi"
        >
          <span class="text-xs font-bold">KNN</span>
        </button>

        <button 
          @click="selectTab('aco')"
          class="p-2.5 rounded-xl transition-all flex flex-col items-center"
          :class="store.activeAlgoTab === 'aco' ? 'bg-red-600/30 text-red-400 border border-red-500/50' : 'text-slate-400 hover:text-white'"
          title="Tahap 2: ACO Optimasi Rute"
        >
          <span class="text-xs font-bold">ACO</span>
        </button>

        <button 
          @click="selectTab('compare')"
          class="p-2.5 rounded-xl transition-all flex flex-col items-center"
          :class="store.activeAlgoTab === 'compare' ? 'bg-emerald-600/30 text-emerald-400 border border-emerald-500/50' : 'text-slate-400 hover:text-white'"
          title="Tahap 3: Uji Perbandingan"
        >
          <span class="text-xs font-bold">EVAL</span>
        </button>
      </div>

      <div class="text-[9px] text-slate-500 font-mono text-center">
        v1.0
      </div>
    </div>

    <!-- Expanded Body (Width covers 50% screen) -->
    <div 
      v-show="store.isLeftPanelExpanded"
      class="flex-1 h-full bg-white flex flex-col overflow-hidden text-slate-800 shadow-2xl"
    >
      <!-- Panel Header -->
      <div class="px-6 py-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
        <div>
          <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <span>🔬 Eksplorasi & Tahapan Algoritma</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-semibold">Deep Transparency</span>
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">Penjelasan matematis, alur perhitungan, dan metrik konvergensi per langkah.</p>
        </div>

        <button 
          @click="store.isLeftPanelExpanded = false"
          class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Tab Navigation -->
      <div class="flex border-b border-slate-200 bg-white px-6">
        <button 
          @click="store.activeAlgoTab = 'knn'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.activeAlgoTab === 'knn' ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>🎯</span>
          <span>1. Alokasi KNN</span>
          <span v-if="store.knnSteps.length > 0" class="px-1.5 py-0.2 bg-indigo-100 text-indigo-700 rounded-full text-[10px]">
            {{ store.knnSteps.length }}
          </span>
        </button>

        <button 
          @click="store.activeAlgoTab = 'aco'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.activeAlgoTab === 'aco' ? 'border-red-600 text-red-600 bg-red-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>🐜</span>
          <span>2. Optimasi Rute ACO</span>
          <span v-if="store.isRouteStarted" class="w-2 h-2 rounded-full bg-emerald-500"></span>
        </button>

        <button 
          @click="store.activeAlgoTab = 'compare'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.activeAlgoTab === 'compare' ? 'border-emerald-600 text-emerald-600 bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>📊</span>
          <span>3. Evaluasi & Perbandingan</span>
        </button>
      </div>

      <!-- Tab Content Area (Scrollable) -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- =================== TAB 1: KNN =================== -->
        <div v-if="store.activeAlgoTab === 'knn'" class="space-y-6">
          <!-- Mathematical Principle Card -->
          <div class="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-4 text-xs space-y-2">
            <div class="font-bold text-indigo-900 flex items-center gap-1.5">
              <span>📐</span>
              <span>Rumus & Prinsip Alokasi K-Nearest Neighbors (KNN)</span>
            </div>
            <p class="text-indigo-800 leading-relaxed">
              Titik acuan kurir berfungsi sebagai <strong>data latih</strong> terlabel. Jarak paket ke setiap titik acuan dihitung berdasarkan jaringan jalan kendaraan dari <strong>OSRM</strong>, lalu scikit-learn mencari <strong>k = {{ store.effectiveK }}</strong> tetangga terdekat. Kurir pemenang ditentukan berdasarkan suara terbanyak. Jika terjadi seri, pemenang ditentukan berdasarkan akumulasi bobot jarak terbalik:
            </p>
            <div class="bg-white/80 border border-indigo-200 rounded-lg p-2.5 font-mono text-[11px] text-indigo-950 flex justify-between items-center">
              <span>w_i = 1 / (Jarak_km + 10^-7)</span>
              <span class="text-slate-500 text-[10px]">Pemberian suara berbobot</span>
            </div>
            <div v-if="store.knnParams.balanceLoad" class="bg-amber-50 border border-amber-200 rounded-lg p-2 text-amber-800 text-[11px]">
              ⚖️ <strong>Opsi Seimbangkan Beban Aktif:</strong> Kapasitas kuota per kurir dibatasi maksimal <code>ceil(N / M)</code>. Paket yang melampaui kuota dialihkan ke kurir terdekat berikutnya.
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="store.knnSteps.length === 0" class="text-center py-12 text-slate-400">
            <div class="text-4xl mb-3">📍</div>
            <p class="font-semibold text-slate-600">Belum Ada Hasil Alokasi KNN</p>
            <p class="text-xs text-slate-400 mt-1">Tekan tombol <strong>Hitung Rute</strong> di panel bawah untuk menjalankan alokasi.</p>
          </div>

          <!-- Package Step Details -->
          <div v-else class="space-y-4">
            <!-- Package Selector Pill Bar -->
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-2">Pilih Paket untuk Melihat Rincian Perhitungan:</label>
              <div class="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto p-1 bg-slate-50 border border-slate-200 rounded-xl">
                <button 
                  v-for="step in store.knnSteps" 
                  :key="step.package_id"
                  @click="store.selectedStepPackageId = step.package_id"
                  class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all"
                  :class="store.selectedStepPackageId === step.package_id 
                    ? 'bg-indigo-600 text-white shadow-sm' 
                    : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'"
                >
                  {{ step.package_id }}
                </button>
              </div>
            </div>

            <!-- Selected Package Deep Dive -->
            <div v-if="activeStep" class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm space-y-4">
              <!-- Header Details -->
              <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 class="font-extrabold text-sm text-slate-900">{{ activeStep.package_name }} ({{ activeStep.package_id }})</h3>
                  <p class="text-xs text-slate-400">Koordinat: {{ activeStep.package_lat.toFixed(5) }}, {{ activeStep.package_lng.toFixed(5) }}</p>
                </div>
                <div class="text-right">
                  <span class="text-[11px] text-slate-500 block">Pemenang Alokasi:</span>
                  <span 
                    class="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold text-white shadow-sm"
                    :style="{ background: getCourierColor(activeStep.winner_courier_id) }"
                  >
                    {{ getCourierName(activeStep.winner_courier_id) }}
                  </span>
                </div>
              </div>

              <!-- Rebalance Alert if any -->
              <div v-if="activeStep.rebalanced" class="bg-amber-50 border border-amber-300 rounded-xl p-3 text-xs text-amber-800">
                <strong>🔄 Penyeimbangan Beban Terjadi:</strong> {{ activeStep.rebalanced_reason }}
              </div>

              <!-- Top-k Neighbors Voting Table -->
              <div>
                <h4 class="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5">
                  <span>🏆</span>
                  <span>{{ store.effectiveK }} Titik Acuan Terdekat (Top-k):</span>
                </h4>
                <div class="overflow-x-auto rounded-xl border border-slate-200">
                  <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                      <tr>
                        <th class="p-2.5">Peringkat</th>
                        <th class="p-2.5">Titik Acuan</th>
                        <th class="p-2.5">Kurir Pemilik</th>
                        <th class="p-2.5">Jarak Jalan (OSRM)</th>
                        <th class="p-2.5">Bobot (1/d)</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                      <tr 
                        v-for="(n, i) in activeStep.top_k" 
                        :key="n.ref_point_id"
                        class="hover:bg-slate-50"
                      >
                        <td class="p-2.5 font-bold text-slate-400">#{{ i + 1 }}</td>
                        <td class="p-2.5 font-semibold text-slate-800">{{ n.ref_point_id }}</td>
                        <td class="p-2.5 font-bold" :style="{ color: getCourierColor(n.courier_id) }">
                          {{ getCourierName(n.courier_id) }}
                        </td>
                        <td class="p-2.5 font-mono text-slate-700">{{ n.distance_km }} km</td>
                        <td class="p-2.5 font-mono text-indigo-600 font-semibold">{{ n.weight.toFixed(4) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Voting Summary -->
              <div class="grid grid-cols-2 gap-3 pt-2">
                <div class="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs">
                  <div class="font-bold text-slate-600 mb-1">Perolehan Suara (Voting):</div>
                  <div v-for="(v, cid) in activeStep.vote_counts" :key="cid" class="flex justify-between py-1">
                    <span :style="{ color: getCourierColor(cid) }" class="font-semibold">{{ getCourierName(cid) }}:</span>
                    <span class="font-bold">{{ v }} suara</span>
                  </div>
                </div>

                <div class="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs">
                  <div class="font-bold text-slate-600 mb-1">Akumulasi Bobot (Tie-breaker):</div>
                  <div v-for="(w, cid) in activeStep.vote_weights" :key="cid" class="flex justify-between py-1">
                    <span :style="{ color: getCourierColor(cid) }" class="font-semibold">{{ getCourierName(cid) }}:</span>
                    <span class="font-bold font-mono">{{ w.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rebalancing Logs List -->
            <div v-if="store.knnRebalanceLogs.length > 0" class="border border-slate-200 rounded-xl p-4 bg-slate-50 text-xs space-y-2">
              <h4 class="font-bold text-slate-800">📋 Catatan Penyeimbangan Beban (Load Balancing Log):</h4>
              <ul class="space-y-1 text-slate-600 font-mono text-[11px]">
                <li v-for="(log, idx) in store.knnRebalanceLogs" :key="idx" class="flex items-start gap-1.5">
                  <span class="text-amber-500">▸</span>
                  <span>{{ log }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- =================== TAB 2: ACO =================== -->
        <div v-else-if="store.activeAlgoTab === 'aco'" class="space-y-6">
          <!-- Mathematical Principle Card -->
          <div class="bg-red-50/70 border border-red-100 rounded-2xl p-4 text-xs space-y-2">
            <div class="font-bold text-red-900 flex items-center gap-1.5">
              <span>🐜</span>
              <span>Rumus & Prinsip Ant Colony Optimization (Open TSP)</span>
            </div>
            <p class="text-red-800 leading-relaxed">
              Masing-masing kelompok paket kurir diselesaikan sebagai <strong>Traveling Salesman Problem Terbuka</strong> (mulai dari depot/posisi kurir, tanpa jarak kembali). Semut memilih titik berikutnya dengan probabilitas gabungan feromon (&alpha;) dan heuristik visibilitas (&beta;):
            </p>
            <div class="bg-white/80 border border-red-200 rounded-lg p-2.5 font-mono text-[11px] text-red-950 flex justify-between items-center">
              <span>P_ij = (tau_ij^alpha * eta_ij^beta) / Sigma(...)</span>
              <span class="text-slate-500 text-[10px]">Peluang Transisi Probabilistik</span>
            </div>
            <p class="text-[11px] text-red-700">
              Pembaruan feromon tiap iterasi: <code>tau_ij &larr; (1 - rho) * tau_ij + Sigma (Q / L_k)</code>
            </p>
          </div>

          <!-- Empty State -->
          <div v-if="!store.isRouteStarted" class="text-center py-12 text-slate-400">
            <div class="text-4xl mb-3">🗺️</div>
            <p class="font-semibold text-slate-600">Belum Ada Rute yang Dihitung</p>
            <p class="text-xs text-slate-400 mt-1">Tekan tombol <strong>Hitung Rute</strong> di panel bawah untuk menjalankan optimasi ACO.</p>
          </div>

          <!-- Courier ACO Inspector -->
          <div v-else class="space-y-5">
            <!-- Select Courier Tab Bar -->
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-2">Pilih Kurir untuk Melihat Progres ACO:</label>
              <div class="flex gap-2">
                <button 
                  v-for="c in store.couriers" 
                  :key="c.id"
                  @click="store.selectedCourierForAco = c.id"
                  class="flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2"
                  :style="store.selectedCourierForAco === c.id 
                    ? { background: c.color, color: 'white', borderColor: c.color } 
                    : { background: 'white', color: '#475569', borderColor: '#e2e8f0' }"
                >
                  <span>🛵</span>
                  <span>{{ c.name }}</span>
                </button>
              </div>
            </div>

            <!-- Courier ACO Details -->
            <div v-if="activeAcoState" class="space-y-4">
              <!-- Summary Card -->
              <div class="grid grid-cols-3 gap-3">
                <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
                  <span class="text-[11px] text-slate-500 block">Total Jarak Rencana</span>
                  <span class="text-base font-black text-slate-900 font-mono">
                    {{ (activeAcoState.totalPlannedM / 1000).toFixed(2) }} km
                  </span>
                </div>
                <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
                  <span class="text-[11px] text-slate-500 block">Jarak Ditempuh</span>
                  <span class="text-base font-black text-emerald-600 font-mono">
                    {{ (activeAcoState.traveledM / 1000).toFixed(2) }} km
                  </span>
                </div>
                <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
                  <span class="text-[11px] text-slate-500 block">Sisa Paket</span>
                  <span class="text-base font-black text-indigo-600 font-mono">
                    {{ activeAcoState.remainingPackageIds.length }}
                  </span>
                </div>
              </div>

              <!-- Convergence Chart -->
              <div class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm">
                <h4 class="text-xs font-bold text-slate-800 mb-2 flex items-center justify-between">
                  <span class="flex items-center gap-1.5">
                    <span>📈</span>
                    <span>Grafik Konvergensi Jarak ACO per Iterasi:</span>
                  </span>
                  <span class="text-[10px] text-slate-400 font-mono">Iterasi 1 s.d. {{ store.acoParams.iterations }}</span>
                </h4>

                <!-- SVG Convergence Plot -->
                <div v-if="activeAcoState.convergence && activeAcoState.convergence.length > 0" class="h-44 w-full pt-2">
                  <svg class="w-full h-full overflow-visible" viewBox="0 0 500 150">
                    <!-- Grid Lines -->
                    <line x1="40" y1="10" x2="480" y2="10" stroke="#f1f5f9" stroke-width="1" />
                    <line x1="40" y1="70" x2="480" y2="70" stroke="#f1f5f9" stroke-width="1" />
                    <line x1="40" y1="130" x2="480" y2="130" stroke="#e2e8f0" stroke-width="1" />

                    <!-- Y-Axis Labels -->
                    <text x="35" y="14" fill="#94a3b8" font-size="9" text-anchor="end">
                      {{ (Math.max(...activeAcoState.convergence) / 1000).toFixed(1) }}k
                    </text>
                    <text x="35" y="134" fill="#94a3b8" font-size="9" text-anchor="end">
                      {{ (Math.min(...activeAcoState.convergence) / 1000).toFixed(1) }}k
                    </text>

                    <!-- Polyline Curve -->
                    <polyline 
                      fill="none" 
                      :stroke="getCourierColor(store.selectedCourierForAco)" 
                      stroke-width="2.5" 
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      :points="getConvergencePoints(activeAcoState.convergence)"
                    />
                  </svg>
                </div>
              </div>

              <!-- Iteration Milestones Table -->
              <div class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm">
                <h4 class="text-xs font-bold text-slate-800 mb-2 flex items-center gap-1.5">
                  <span>⏱️</span>
                  <span>Catatan Iterasi ACO (Milestone Log):</span>
                </h4>
                <div class="overflow-x-auto rounded-xl border border-slate-200">
                  <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                      <tr>
                        <th class="p-2.5">Iterasi</th>
                        <th class="p-2.5">Jarak Terbaik (km)</th>
                        <th class="p-2.5">Rata-rata Semut (km)</th>
                        <th class="p-2.5">Urutan Tur Terbaik</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                      <tr v-for="log in activeAcoState.acoLogs" :key="log.iteration" class="hover:bg-slate-50">
                        <td class="p-2.5 font-bold text-slate-700">#{{ log.iteration }}</td>
                        <td class="p-2.5 font-bold text-emerald-600">{{ (log.best_distance_m / 1000).toFixed(3) }}</td>
                        <td class="p-2.5 text-slate-500">{{ (log.avg_distance_m / 1000).toFixed(3) }}</td>
                        <td class="p-2.5 text-slate-700 truncate max-w-xs">{{ log.best_tour.join(' → ') }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- =================== TAB 3: COMPARE =================== -->
        <div v-else-if="store.activeAlgoTab === 'compare'" class="space-y-6">
          <div class="bg-emerald-50/70 border border-emerald-100 rounded-2xl p-4 text-xs space-y-2">
            <div class="font-bold text-emerald-900 flex items-center gap-1.5">
              <span>📊</span>
              <span>Uji Perbandingan Akademik & Evaluasi Kinerja (FR-17)</span>
            </div>
            <p class="text-emerald-800 leading-relaxed">
              Membandingkan kualitas metode alokasi (<strong>KNN</strong> vs <strong>K-Means</strong> vs <strong>Acak</strong>) dan metode pengurutan rute (<strong>ACO</strong> vs <strong>Nearest Neighbor</strong> vs <strong>Urutan Klik</strong>) untuk membuktikan efisiensi jarak dan pemerataan beban.
            </p>
            <button 
              @click="store.runComparison()"
              :disabled="store.packages.length === 0 || store.isCalculating"
              class="mt-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-4 rounded-xl text-xs shadow-md transition-all flex items-center gap-2"
            >
              <span>{{ store.isCalculating ? 'Sedang Memproses...' : 'Jalankan Evaluasi Komparatif' }}</span>
              <span>⚡</span>
            </button>
          </div>

          <!-- Empty State -->
          <div v-if="!store.comparisonData" class="text-center py-12 text-slate-400">
            <div class="text-4xl mb-3">📈</div>
            <p class="font-semibold text-slate-600">Data Evaluasi Belum Tersedia</p>
            <p class="text-xs text-slate-400 mt-1">Tekan tombol <strong>Jalankan Evaluasi Komparatif</strong> di atas.</p>
          </div>

          <!-- Comparison Tables -->
          <div v-else class="space-y-6">
            <!-- Table 1: Allocation Comparison -->
            <div class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm space-y-3">
              <h4 class="text-xs font-extrabold text-slate-900 flex items-center gap-1.5">
                <span>📍</span>
                <span>Perbandingan Metode Alokasi Paket</span>
              </h4>
              <div class="overflow-x-auto rounded-xl border border-slate-200">
                <table class="w-full text-left text-xs">
                  <thead class="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th class="p-2.5">Metode Alokasi</th>
                      <th class="p-2.5">Total Jarak (km)</th>
                      <th class="p-2.5">Jarak Maks Kurir (km)</th>
                      <th class="p-2.5">Standar Deviasi Beban</th>
                      <th class="p-2.5">Waktu (ms)</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                    <tr 
                      v-for="res in store.comparisonData.allocation_comparisons" 
                      :key="res.name"
                      :class="res.name.includes('KNN') ? 'bg-indigo-50/40 font-bold' : ''"
                    >
                      <td class="p-2.5 font-sans font-semibold text-slate-800">{{ res.name }}</td>
                      <td class="p-2.5 text-indigo-700 font-bold">{{ (res.total_distance_m / 1000).toFixed(2) }}</td>
                      <td class="p-2.5 text-slate-700">{{ (res.max_courier_distance_m / 1000).toFixed(2) }}</td>
                      <td class="p-2.5 text-slate-700">{{ res.std_dev_packages }}</td>
                      <td class="p-2.5 text-slate-500">{{ res.execution_time_ms }} ms</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Table 2: Routing Comparison -->
            <div class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm space-y-3">
              <h4 class="text-xs font-extrabold text-slate-900 flex items-center gap-1.5">
                <span>🛣️</span>
                <span>Perbandingan Metode Pengurutan Rute (Routing)</span>
              </h4>
              <div class="overflow-x-auto rounded-xl border border-slate-200">
                <table class="w-full text-left text-xs">
                  <thead class="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th class="p-2.5">Metode Rute</th>
                      <th class="p-2.5">Total Jarak</th>
                      <th class="p-2.5">Hemat vs Klik</th>
                      <th class="p-2.5">Hemat vs NN</th>
                      <th class="p-2.5">Waktu (ms)</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                    <tr 
                      v-for="res in store.comparisonData.routing_comparisons" 
                      :key="res.method"
                      :class="res.method.includes('ACO') ? 'bg-red-50/40 font-bold' : ''"
                    >
                      <td class="p-2.5 font-sans font-semibold text-slate-800">{{ res.method }}</td>
                      <td class="p-2.5 text-red-700 font-bold">{{ res.total_distance_km }} km</td>
                      <td class="p-2.5 text-emerald-600 font-bold">+{{ res.savings_vs_click_percent }}%</td>
                      <td class="p-2.5 text-blue-600 font-bold">+{{ res.savings_vs_nn_percent }}%</td>
                      <td class="p-2.5 text-slate-500">{{ res.execution_time_ms }} ms</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

function selectTab(tab) {
  store.activeAlgoTab = tab
  store.isLeftPanelExpanded = true
}

const activeStep = computed(() => {
  if (!store.knnSteps.length) return null
  return store.knnSteps.find(s => s.package_id === store.selectedStepPackageId) || store.knnSteps[0]
})

const activeAcoState = computed(() => {
  return store.courierStates[store.selectedCourierForAco] || null
})

function getCourierName(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.name : courierId
}

function getCourierColor(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.color : '#3B82F6'
}

function getConvergencePoints(data) {
  if (!data || data.length === 0) return ''
  const minVal = Math.min(...data)
  const maxVal = Math.max(...data)
  const range = maxVal - minVal || 1.0

  const width = 440
  const height = 120
  const startX = 40
  const startY = 10

  return data.map((val, idx) => {
    const x = startX + (idx / (data.length - 1 || 1)) * width
    const normalizedY = (val - minVal) / range
    const y = startY + (1 - normalizedY) * height
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}
</script>
