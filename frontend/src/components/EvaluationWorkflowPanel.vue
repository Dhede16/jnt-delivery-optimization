<template>
  <div
    class="algorithm-panel fixed top-0 left-0 bottom-0 z-30 flex transition-all duration-200 ease-in-out select-none"
    :class="isPanelExpanded ? ['w-[50vw]', 'min-w-[420px]', 'max-w-[700px]', 'is-expanded'] : ['w-16', 'is-collapsed']"
  >
    <!-- Collapsed Slim Vertical Sidebar (Matches main page exactly) -->
    <div 
      class="algorithm-sidebar w-16 h-full flex flex-col items-center py-5 justify-between text-white select-none z-20 shrink-0 bg-slate-900"
    >
      <div class="flex flex-col items-center space-y-6">
        <!-- Toggle Expand Button -->
        <button 
          @click="isPanelExpanded = !isPanelExpanded"
          aria-label="Buka atau tutup panel algoritma evaluasi"
          class="p-2.5 rounded-xl text-slate-300 hover:text-white transition-all flex flex-col items-center"
          :title="isPanelExpanded ? 'Kecilkan Panel' : 'Perlebar Tahapan Algoritma'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <rect x="4" y="5" width="16" height="14" rx="2" stroke-width="2" />
            <path d="M9 5v14" stroke-width="2" />
          </svg>
          <span class="text-[9px] mt-1 font-semibold text-slate-400">
            {{ isPanelExpanded ? 'Tutup' : 'Buka' }}
          </span>
        </button>

        <div class="w-8 h-px bg-slate-800"></div>

        <!-- Quick Tab Nav Icons -->
        <button 
          @click="selectTab('knn')"
          class="p-2.5 rounded-xl transition-all flex flex-col items-center"
          :class="activeTab === 'knn' && isPanelExpanded ? 'bg-white/20 text-white border border-white/40' : 'text-blue-100 hover:text-white'"
          title="Tahap 1: KNN Alokasi"
        >
          <span class="text-xs font-bold">KNN</span>
        </button>

        <button 
          @click="selectTab('routing')"
          class="p-2.5 rounded-xl transition-all flex flex-col items-center"
          :class="activeTab === 'routing' && isPanelExpanded ? 'bg-white/20 text-white border border-white/40' : 'text-blue-100 hover:text-white'"
          :title="'Tahap 2: Rute ' + displayMethodName"
        >
          <span class="text-xs font-bold">{{ methodBadgeText }}</span>
        </button>
      </div>

      <div class="text-[9px] text-slate-500 font-mono text-center">
        EVAL
      </div>
    </div>

    <!-- Expanded Body (Width covers up to 50% screen, styled identically to main page) -->
    <div 
      v-show="isPanelExpanded"
      class="algorithm-content flex-1 h-full flex flex-col overflow-hidden text-slate-800 bg-white shadow-2xl border-r border-slate-200"
    >
      <!-- Panel Header -->
      <div class="px-6 py-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
        <div>
          <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <span>🔬 Eksplorasi & Tahapan Algoritma</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700 font-bold">
              Simulasi {{ displayMethodName }}
            </span>
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">Penjelasan matematis, alur perhitungan langkah demi langkah, dan evaluasi rute.</p>
        </div>

        <button 
          @click="isPanelExpanded = false"
          class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition-colors"
          title="Tutup panel"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Tab Navigation -->
      <div class="flex border-b border-slate-200 bg-white px-6">
        <button 
          @click="activeTab = 'knn'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="activeTab === 'knn' ? 'border-indigo-600 text-indigo-700 bg-indigo-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>🎯</span>
          <span>1. Alokasi KNN</span>
          <span v-if="store.knnSteps.length > 0" class="px-1.5 py-0.2 bg-indigo-100 text-indigo-700 rounded-full text-[10px]">
            {{ store.knnSteps.length }}
          </span>
        </button>

        <button 
          @click="activeTab = 'routing'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="activeTab === 'routing' ? 'border-indigo-600 text-indigo-700 bg-indigo-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>🛣️</span>
          <span>2. Rute {{ displayMethodName }}</span>
          <span v-if="activeCourierSteps.length > 0" class="px-1.5 py-0.2 bg-emerald-100 text-emerald-700 rounded-full text-[10px] font-mono">
            {{ activeCourierSteps.length }} titik
          </span>
        </button>
      </div>

      <!-- Tab Content Area (Scrollable) -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- =================== TAB 1: KNN ALLOCATION =================== -->
        <div v-if="activeTab === 'knn'" class="space-y-6">
          <!-- Mathematical Principle Card -->
          <div class="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-4 text-xs space-y-2">
            <div class="font-bold text-indigo-900 flex items-center gap-1.5">
              <span>📐</span>
              <span>Rumus & Prinsip Alokasi K-Nearest Neighbors (KNN)</span>
            </div>
            <p class="text-indigo-800 leading-relaxed">
              Jarak jalan raya (OSRM) dihitung antara paket dengan semua titik acuan kurir. Sebanyak <strong>k = {{ store.effectiveK }}</strong> titik acuan terdekat memberikan suara menggunakan pembobotan terbalik (<em>inverse distance weighting</em>):
            </p>
            <div class="bg-white/80 border border-indigo-200 rounded-lg p-2.5 font-mono text-[11px] text-indigo-950 flex justify-between items-center">
              <span>w_i = 1 / (d_i + &epsilon;)</span>
              <span class="text-slate-500 text-[10px]">&epsilon; = 1e-7 (mencegah pembagian nol)</span>
            </div>
            <div v-if="store.knnParams.balanceLoad" class="bg-amber-50 border border-amber-200 rounded-lg p-2 text-amber-800 text-[11px]">
              ⚖️ <strong>Penyeimbangan Beban Aktif:</strong> Beban paket dibatasi rata (maks &lceil;N/M&rceil; paket per kurir) untuk mencegah penumpukan paket pada satu kurir.
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="store.knnSteps.length === 0" class="text-center py-12 text-slate-400">
            <div class="text-4xl mb-3">📦</div>
            <p class="font-semibold text-slate-600">Belum Ada Hasil Alokasi KNN</p>
            <p class="text-xs text-slate-400 mt-1">Data alokasi paket KNN akan ditampilkan saat perhitungan selesai.</p>
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
                  @click="selectedStepPackageId = step.package_id"
                  class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all"
                  :class="activePackageId === step.package_id 
                    ? 'bg-indigo-600 text-white shadow-sm' 
                    : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'"
                >
                  {{ step.package_id }}
                </button>
              </div>
            </div>

            <!-- Selected Package Deep Dive -->
            <div v-if="activeKnnStep" class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm space-y-4">
              <!-- Header Details -->
              <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 class="font-extrabold text-sm text-slate-900">{{ activeKnnStep.package_name }} ({{ activeKnnStep.package_id }})</h3>
                  <p class="text-xs text-slate-400">Koordinat: {{ activeKnnStep.package_lat.toFixed(5) }}, {{ activeKnnStep.package_lng.toFixed(5) }}</p>
                </div>
                <div class="text-right">
                  <span class="text-[11px] text-slate-500 block">Pemenang Alokasi:</span>
                  <span 
                    class="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold text-white shadow-sm"
                    :style="{ background: getCourierColor(activeKnnStep.winner_courier_id) }"
                  >
                    {{ getCourierName(activeKnnStep.winner_courier_id) }}
                  </span>
                </div>
              </div>

              <!-- Rebalance Alert if any -->
              <div v-if="activeKnnStep.rebalanced" class="bg-amber-50 border border-amber-300 rounded-xl p-3 text-xs text-amber-800">
                <strong>🔄 Penyeimbangan Beban Terjadi:</strong> {{ activeKnnStep.rebalanced_reason }}
              </div>

              <!-- Ranked reference points -->
              <div>
                <h4 class="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5">
                  <span>🏆</span>
                  <span>Urutan Semua Titik Acuan ({{ store.effectiveK }} teratas dipakai untuk menentukan kurir):</span>
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
                        <th class="p-2.5">Dipakai</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                      <tr 
                        v-for="(n, i) in activeKnnStep.all_distances"
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
                        <td class="p-2.5 font-semibold" :class="activeKnnStep.top_k.some(item => item.ref_point_id === n.ref_point_id) ? 'text-emerald-700 font-bold' : 'text-slate-400'">
                          {{ activeKnnStep.top_k.some(item => item.ref_point_id === n.ref_point_id) ? 'Ya' : 'Tidak' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Voting Summary -->
              <div class="grid grid-cols-2 gap-3 pt-2">
                <div class="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs">
                  <div class="font-bold text-slate-600 mb-1">Perolehan Suara (Voting):</div>
                  <div v-for="(v, cid) in activeKnnStep.vote_counts" :key="cid" class="flex justify-between py-1">
                    <span :style="{ color: getCourierColor(cid) }" class="font-semibold">{{ getCourierName(cid) }}:</span>
                    <span class="font-bold">{{ v }} suara</span>
                  </div>
                </div>

                <div class="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs">
                  <div class="font-bold text-slate-600 mb-1">Akumulasi Bobot (Tie-breaker):</div>
                  <div v-for="(w, cid) in activeKnnStep.vote_weights" :key="cid" class="flex justify-between py-1">
                    <span :style="{ color: getCourierColor(cid) }" class="font-semibold">{{ getCourierName(cid) }}:</span>
                    <span class="font-bold font-mono">{{ w.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rebalance Logs Timeline -->
            <div v-if="store.knnRebalanceLogs.length > 0" class="border border-slate-200 rounded-xl p-4 bg-slate-50 text-xs space-y-2">
              <span class="font-bold text-slate-700 block">Catatan Log Algoritma Penyeimbangan Beban:</span>
              <ul class="space-y-1 text-slate-600">
                <li v-for="(log, idx) in store.knnRebalanceLogs" :key="idx" class="flex items-start gap-1.5">
                  <span class="text-amber-500 mt-0.5">•</span>
                  <span>{{ log }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- =================== TAB 2: ROUTING METHOD STEPS =================== -->
        <div v-else-if="activeTab === 'routing'" class="space-y-6">
          <!-- Method Mathematical Principle Card -->
          <div class="border rounded-2xl p-4 text-xs space-y-2" :class="methodExplanation.boxClass">
            <div class="font-bold flex items-center gap-1.5" :class="methodExplanation.titleClass">
              <span>{{ methodExplanation.icon }}</span>
              <span>{{ methodExplanation.title }}</span>
            </div>
            <p class="leading-relaxed opacity-95">
              {{ methodExplanation.description }}
            </p>
            <div class="bg-white/85 border rounded-lg p-2.5 font-mono text-[11px] flex justify-between items-center" :class="methodExplanation.codeBorder">
              <span>{{ methodExplanation.formula }}</span>
              <span class="text-slate-500 text-[10px]">{{ methodExplanation.formulaLabel }}</span>
            </div>
            <p class="text-[11px] opacity-80">
              {{ methodExplanation.note }}
            </p>
          </div>

          <!-- Select Courier Tab Bar -->
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-2">Pilih Kurir untuk Melihat Rincian Rute:</label>
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="c in availableCouriers" 
                :key="c.id"
                @click="selectedCourierId = c.id"
                class="flex-1 min-w-[120px] py-2 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2"
                :style="activeCourierId === c.id 
                  ? { background: c.color, color: 'white', borderColor: c.color } 
                  : { background: 'white', color: '#475569', borderColor: '#e2e8f0' }"
              >
                <span>🛵</span>
                <span>{{ c.name }}</span>
              </button>
            </div>
          </div>

          <!-- Summary Metric Cards -->
          <div class="grid grid-cols-3 gap-3">
            <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
              <span class="text-[11px] text-slate-500 block">Total Jarak Rute</span>
              <span class="text-base font-black text-slate-900 font-mono">
                {{ totalCourierDistanceKm }} km
              </span>
            </div>
            <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
              <span class="text-[11px] text-slate-500 block">Total Titik Dikunjungi</span>
              <span class="text-base font-black text-indigo-600 font-mono">
                {{ activeCourierSteps.length }} titik
              </span>
            </div>
            <div class="bg-slate-50 border border-slate-200 p-3 rounded-xl text-center">
              <span class="text-[11px] text-slate-500 block">Metode Evaluasi</span>
              <span class="text-xs font-extrabold text-slate-800">
                {{ displayMethodName }}
              </span>
            </div>
          </div>

          <!-- ACO Convergence & Iterations (if ACO) -->
          <div v-if="isAco && activeAcoDetails" class="space-y-4">
            <div v-if="activeAcoDetails.convergence && activeAcoDetails.convergence.length > 0" class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm">
              <h4 class="text-xs font-bold text-slate-800 mb-2 flex items-center justify-between">
                <span class="flex items-center gap-1.5">
                  <span>📈</span>
                  <span>Grafik Konvergensi Jarak ACO per Iterasi:</span>
                </span>
                <span class="text-[10px] text-slate-400 font-mono">Iterasi 1 s.d. {{ store.acoParams.iterations }}</span>
              </h4>
              <div class="h-44 w-full pt-2">
                <svg class="w-full h-full overflow-visible" viewBox="0 0 500 150">
                  <line x1="40" y1="10" x2="480" y2="10" stroke="#f1f5f9" stroke-width="1" />
                  <line x1="40" y1="70" x2="480" y2="70" stroke="#f1f5f9" stroke-width="1" />
                  <line x1="40" y1="130" x2="480" y2="130" stroke="#e2e8f0" stroke-width="1" />
                  <text x="35" y="14" fill="#94a3b8" font-size="9" text-anchor="end">
                    {{ (Math.max(...activeAcoDetails.convergence) / 1000).toFixed(1) }}k
                  </text>
                  <text x="35" y="134" fill="#94a3b8" font-size="9" text-anchor="end">
                    {{ (Math.min(...activeAcoDetails.convergence) / 1000).toFixed(1) }}k
                  </text>
                  <polyline 
                    fill="none" 
                    :stroke="getCourierColor(activeCourierId)" 
                    stroke-width="2.5" 
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    :points="getConvergencePoints(activeAcoDetails.convergence)"
                  />
                </svg>
              </div>
            </div>

            <div v-if="activeAcoDetails.iterations_log && activeAcoDetails.iterations_log.length > 0" class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm">
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
                      <th class="p-2.5">Urutan Tur Terbaik</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                    <tr v-for="log in activeAcoDetails.iterations_log" :key="log.iteration" class="hover:bg-slate-50">
                      <td class="p-2.5 font-bold text-slate-700">#{{ log.iteration }}</td>
                      <td class="p-2.5 font-bold text-emerald-600">{{ (log.best_distance_m / 1000).toFixed(3) }}</td>
                      <td class="p-2.5 text-slate-700 truncate max-w-xs">{{ log.best_tour?.join(' → ') }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Step-by-Step Chronological Calculations Table & Cards -->
          <div class="border border-slate-200 rounded-2xl p-4 bg-white shadow-sm space-y-4">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <h4 class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <span>📍</span>
                <span>Rincian Perhitungan Rute Langkah Demi Langkah (Step-by-Step):</span>
              </h4>
              <span class="text-[10px] text-slate-400 font-mono">Titik Awal: Depot Juanda</span>
            </div>

            <div v-if="activeCourierSteps.length === 0" class="py-8 text-center text-xs text-slate-400">
              Tidak ada paket yang dialokasikan untuk kurir ini.
            </div>

            <!-- Steps List -->
            <div v-else class="space-y-3">
              <div
                v-for="step in activeCourierSteps"
                :key="step.step"
                class="border border-slate-200 rounded-xl p-3.5 bg-slate-50/70 hover:bg-slate-50 transition-all space-y-2.5"
              >
                <!-- Step Main Line -->
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="w-6 h-6 rounded-full bg-indigo-600 text-white font-extrabold text-xs flex items-center justify-center shadow-sm">
                      {{ step.step }}
                    </span>
                    <div>
                      <span class="text-xs font-extrabold text-slate-900">
                        {{ step.from_name }} 
                        <span class="text-indigo-600 mx-1">➔</span> 
                        <span class="text-emerald-700">{{ step.to_name }}</span>
                      </span>
                      <span class="block text-[10px] text-slate-400">ID: {{ step.from_id }} ➔ {{ step.to_id }}</span>
                    </div>
                  </div>
                  <div class="text-right">
                    <span class="font-mono text-xs font-extrabold text-slate-900 block">+{{ step.distance_km }} km</span>
                    <span class="text-[10px] text-slate-500 font-mono">Kumulatif: {{ step.cumulative_distance_km }} km</span>
                  </div>
                </div>

                <!-- Candidates Evaluation (Nearest Neighbor & Dijkstra) -->
                <div v-if="step.candidates && step.candidates.length > 0" class="pt-2 border-t border-slate-200">
                  <div class="flex items-center justify-between mb-1.5">
                    <span class="text-[11px] font-bold text-slate-700 flex items-center gap-1">
                      <span>🔍</span>
                      <span>Evaluasi Perbandingan Jarak Titik Kandidat ({{ step.candidates.length }} titik diuji):</span>
                    </span>
                    <span class="text-[10px] text-indigo-700 font-semibold">
                      Dipilih: {{ step.to_name }} ({{ step.distance_km }} km)
                    </span>
                  </div>

                  <div class="overflow-x-auto rounded-lg border border-slate-200 bg-white">
                    <table class="w-full text-left text-[11px]">
                      <thead class="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                        <tr>
                          <th class="p-2">Rank</th>
                          <th class="p-2">Titik Paket Kandidat</th>
                          <th class="p-2">Jarak Jalan OSRM</th>
                          <th class="p-2">Status Seleksi</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-100">
                        <tr
                          v-for="(c, cIdx) in step.candidates"
                          :key="c.point_id"
                          :class="c.is_chosen ? 'bg-emerald-50/80 font-bold text-emerald-950' : 'text-slate-600'"
                        >
                          <td class="p-2 font-mono text-slate-400">#{{ cIdx + 1 }}</td>
                          <td class="p-2 font-semibold">
                            {{ c.point_name }}
                            <span class="text-[10px] text-slate-400 font-mono ml-1">({{ c.point_id }})</span>
                          </td>
                          <td class="p-2 font-mono" :class="c.is_chosen ? 'text-emerald-700 font-extrabold' : 'text-slate-700'">
                            {{ c.distance_km !== undefined ? c.distance_km : c.dijkstra_distance_km }} km
                          </td>
                          <td class="p-2">
                            <span v-if="c.is_chosen" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 font-bold">
                              <span>✓</span> Terpilih (Jarak Minimum)
                            </span>
                            <span v-else class="text-slate-400 text-[10px]">-</span>
                          </td>
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
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useAppStore } from '../stores/appStore'

const props = defineProps({
  routingComparison: { type: Object, default: () => ({}) },
  methodName: { type: String, default: '' }
})

const store = useAppStore()
const isPanelExpanded = ref(true)
const activeTab = ref('routing')
const selectedCourierId = ref('')
const selectedStepPackageId = ref('')

function selectTab(tab) {
  activeTab.value = tab
  isPanelExpanded.value = true
}

const displayMethodName = computed(() => {
  if (props.methodName) return props.methodName
  const m = props.routingComparison?.method || ''
  if (m.includes('ACO')) return 'ACO'
  if (m.includes('Nearest Neighbor')) return 'Nearest Neighbor'
  if (m.includes('Dijkstra')) return 'Dijkstra'
  if (m.includes('Urutan Klik')) return 'Urutan Klik'
  return m
})

const methodBadgeText = computed(() => {
  const m = displayMethodName.value
  if (m.includes('Nearest Neighbor')) return 'NN'
  if (m.includes('Dijkstra')) return 'DIJK'
  if (m.includes('ACO')) return 'ACO'
  if (m.includes('Urutan Klik')) return 'KLIK'
  return 'RUTE'
})

const isAco = computed(() => displayMethodName.value.includes('ACO'))

const methodExplanation = computed(() => {
  const name = displayMethodName.value
  if (name.includes('Nearest Neighbor')) {
    return {
      title: 'Prinsip Heuristik Nearest Neighbor (NN)',
      icon: '⚡',
      boxClass: 'bg-amber-50/70 border-amber-200 text-amber-950',
      titleClass: 'text-amber-900',
      codeBorder: 'border-amber-200 text-amber-950',
      formula: 'u* = argmin_{u in unvisited} d(curr, u)',
      formulaLabel: 'Pilihan Rakus (Greedy)',
      description: 'Dari simpul/lokasi saat ini, kurir menghitung jarak ke seluruh paket tersisa dan langsung memilih paket dengan jarak terpendek berikutnya.',
      note: 'Sederhana dan cepat, namun sering terjebak optimum lokal karena tidak mempertimbangkan rute global.'
    }
  }
  if (name.includes('Dijkstra')) {
    return {
      title: 'Prinsip Dijkstra Shortest Path (Greedy)',
      icon: '🔍',
      boxClass: 'bg-violet-50/70 border-violet-200 text-violet-950',
      titleClass: 'text-violet-900',
      codeBorder: 'border-violet-200 text-violet-950',
      formula: 'u* = argmin_{u in unvisited} dist_Dijkstra[u]',
      formulaLabel: 'Relaksasi Graf Berbobot',
      description: 'Menelusuri graf jaringan jalan dengan antrean prioritas (priority queue) untuk mencari akumulasi lintasan terpendek ke seluruh paket unvisited.',
      note: 'Menjamin lintasan terpendek antar dua simpul pada graf jalan, lalu memilih simpul tujuan terdekat berikutnya secara greedy.'
    }
  }
  if (name.includes('ACO')) {
    return {
      title: 'Prinsip Ant Colony Optimization (Open TSP)',
      icon: '🐜',
      boxClass: 'bg-red-50/70 border-red-200 text-red-950',
      titleClass: 'text-red-900',
      codeBorder: 'border-red-200 text-red-950',
      formula: 'P_ij = (tau_ij^alpha * eta_ij^beta) / Sigma(...)',
      formulaLabel: 'Peluang Transisi Semut',
      description: 'Koloni semut tiruan mengeksplorasi graf rute menggunakan jejak feromon (tau) dan informasi heuristik visibilitas jarak (eta = 1/d).',
      note: 'Feromon menguap secara bertahap (rho) dan diperbarui berdasarkan kualitas panjang tur total semut.'
    }
  }
  return {
    title: 'Urutan Input Manual (Kronologis)',
    icon: '📝',
    boxClass: 'bg-slate-50 border-slate-200 text-slate-800',
    titleClass: 'text-slate-900',
    codeBorder: 'border-slate-200 text-slate-950',
    formula: 'Tour = [P_1, P_2, P_3, ..., P_N]',
    formulaLabel: 'Urutan Input Pengguna',
    description: 'Paket dikunjungi berurutan sesuai dengan urutan kronologis saat pengguna menambahkan titik di peta tanpa algoritma optimasi rute.',
    note: 'Digunakan sebagai garis dasar (baseline) untuk mengukur persentase efisiensi dan penghematan jarak algoritma optimasi.'
  }
})

// Couriers in this evaluation
const availableCouriers = computed(() => {
  const routes = props.routingComparison?.routes || []
  if (routes.length === 0) return store.couriers
  const filtered = store.couriers.filter(c => routes.some(r => r.courier_id === c.id))
  return filtered.length > 0 ? filtered : store.couriers
})

const activeCourierId = computed(() => {
  if (selectedCourierId.value && availableCouriers.value.some(c => c.id === selectedCourierId.value)) {
    return selectedCourierId.value
  }
  return availableCouriers.value[0]?.id || ''
})

watch(availableCouriers, (list) => {
  if (list.length > 0 && !list.some(c => c.id === selectedCourierId.value)) {
    selectedCourierId.value = list[0].id
  }
}, { immediate: true })

// Steps calculation (uses backend steps_by_courier, with foolproof frontend calculation fallback)
const activeCourierSteps = computed(() => {
  const cid = activeCourierId.value
  if (!cid) return []

  // 1. Try backend steps
  const backendSteps = props.routingComparison?.steps_by_courier?.[cid]
  if (backendSteps && backendSteps.length > 0) {
    return backendSteps
  }

  // 2. Fallback: compute dynamically from route and points
  const routes = props.routingComparison?.routes || []
  const route = routes.find(r => r.courier_id === cid)
  const tour = route?.package_ids || []
  if (tour.length === 0) return []

  const depot = store.depot
  const pkgMap = new Map(store.packages.map(p => [p.id, p]))
  const idToIdx = new Map((store.pointIds || []).map((id, idx) => [id, idx]))
  const matrix = store.matrix || []

  function getDistanceM(fromId, toId) {
    const fIdx = idToIdx.get(fromId)
    const tIdx = idToIdx.get(toId)
    if (fIdx !== undefined && tIdx !== undefined && matrix[fIdx] && matrix[fIdx][tIdx] !== undefined) {
      return matrix[fIdx][tIdx]
    }
    const p1 = fromId === depot.id ? depot : pkgMap.get(fromId)
    const p2 = toId === depot.id ? depot : pkgMap.get(toId)
    if (p1 && p2) {
      const R = 6371000
      const dLat = (p2.lat - p1.lat) * Math.PI / 180
      const dLng = (p2.lng - p1.lng) * Math.PI / 180
      const a = Math.sin(dLat / 2) ** 2 + Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) * Math.sin(dLng / 2) ** 2
      return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    }
    return 1000
  }

  const steps = []
  let currId = depot.id
  let currName = depot.name || 'Depot Juanda'
  let totalDistM = 0

  tour.forEach((targetId, idx) => {
    const targetPkg = pkgMap.get(targetId)
    const targetName = targetPkg?.name || targetId
    const segDistM = getDistanceM(currId, targetId)
    totalDistM += segDistM

    const remainingIds = tour.slice(idx)
    const candidates = remainingIds.map(candId => {
      const candPkg = pkgMap.get(candId)
      const d = getDistanceM(currId, candId)
      return {
        point_id: candId,
        point_name: candPkg?.name || candId,
        distance_m: Math.round(d * 10) / 10,
        distance_km: (d / 1000).toFixed(3),
        dijkstra_distance_km: (d / 1000).toFixed(3),
        is_chosen: candId === targetId
      }
    })
    candidates.sort((a, b) => a.distance_m - b.distance_m)

    steps.push({
      step: idx + 1,
      from_id: currId,
      from_name: currName,
      to_id: targetId,
      to_name: targetName,
      distance_m: Math.round(segDistM * 10) / 10,
      distance_km: (segDistM / 1000).toFixed(3),
      cumulative_distance_km: (totalDistM / 1000).toFixed(3),
      candidates
    })

    currId = targetId
    currName = targetName
  })

  return steps
})

const activeAcoDetails = computed(() => {
  const cid = activeCourierId.value
  if (!cid) return null
  return props.routingComparison?.aco_details_by_courier?.[cid] || store.courierStates?.[cid] || null
})

const totalCourierDistanceKm = computed(() => {
  const steps = activeCourierSteps.value
  if (!steps.length) return '0.00'
  const last = steps[steps.length - 1]
  return last?.cumulative_distance_km !== undefined ? last.cumulative_distance_km : '0.00'
})

function getConvergencePoints(convergence) {
  if (!convergence || convergence.length === 0) return ''
  const max = Math.max(...convergence)
  const min = Math.min(...convergence)
  const range = max - min || 1
  return convergence.map((val, idx) => {
    const x = 40 + (idx / (convergence.length - 1 || 1)) * 440
    const y = 130 - ((val - min) / range) * 115
    return `${x},${y}`
  }).join(' ')
}

// KNN State
const activePackageId = computed(() => {
  if (selectedStepPackageId.value && store.knnSteps.some(s => s.package_id === selectedStepPackageId.value)) {
    return selectedStepPackageId.value
  }
  return store.selectedStepPackageId || store.knnSteps[0]?.package_id || ''
})

const activeKnnStep = computed(() => {
  if (!store.knnSteps.length) return null
  return store.knnSteps.find(s => s.package_id === activePackageId.value) || store.knnSteps[0]
})

function getCourierName(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.name : courierId
}

function getCourierColor(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.color : '#4F46E5'
}
</script>
