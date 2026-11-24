<template>
  <div 
    class="control-drawer fixed z-20 flex flex-col transition-all duration-500 ease-in-out"
    :class="store.isBottomDrawerOpen ? ['h-[440px]', 'is-open'] : ['h-16', 'is-collapsed']"
  >
    <!-- Drawer Drag / Toggle Handle Bar -->
    <div 
      @click="store.isBottomDrawerOpen = !store.isBottomDrawerOpen"
      class="control-drawer-header relative h-16 px-6 flex items-center justify-between cursor-pointer select-none transition-colors"
    >
      <div class="flex items-center">
        <span class="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 truncate max-w-[130px] sm:max-w-none">
          Panel Masukan Data & Kontrol
        </span>
      </div>

      <!-- Drawer Chevron Indicator -->
      <button
        type="button"
        @click.stop="store.isBottomDrawerOpen = !store.isBottomDrawerOpen"
        :aria-expanded="store.isBottomDrawerOpen"
        aria-label="Buka atau tutup panel masukan dan kontrol"
        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-primary-soft flex items-center justify-center text-primary shadow-sm hover:bg-primary-soft/80 transition-colors"
      >
        <svg 
          class="w-5 h-5 transform transition-transform duration-300" 
          :class="store.isBottomDrawerOpen ? 'rotate-180' : 'rotate-0'"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>
      </button>

      <!-- Quick Metrics Pills & Action Buttons -->
      <div class="flex items-center space-x-3 text-xs" @click.stop>
        <div v-if="store.isRouteStarted" class="flex items-center space-x-2 bg-primary-soft px-3 py-1.5 rounded-xl border border-line text-primary">
          <span>Ditempuh:</span>
          <span class="font-bold font-mono text-ink">{{ store.totalDistanceTraveledKm }} km</span>
          <span class="text-slate-400">/ {{ store.totalDistancePlannedKm }} km</span>
        </div>

        <!-- Action: Hitung Rute -->
        <button 
          v-if="store.canCalculate && !store.isRouteStarted"
          @click="store.calculateRoutes()"
          :disabled="!store.canCalculate"
          class="bg-primary hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed text-ink font-extrabold px-5 py-2 rounded-xl text-xs shadow-lg transition-all flex items-center space-x-2"
        >
          <span>{{ store.isCalculating ? 'Menghitung...' : 'Mulai Simulasi' }}</span>
          <span v-if="!store.isCalculating">🚀</span>
        </button>

        <!-- Action: Step Execution (Lanjut) & Repeat Simulation -->
        <div v-else-if="store.isRouteStarted" class="flex items-center space-x-2">
          <!-- Simulation Finished Status & Repeat Button -->
          <template v-if="store.isSimulationFinished">
            <span class="hidden sm:inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2.5 py-1.5 rounded-xl border border-emerald-300">
              <span>🎉</span> Selesai
            </span>
            <button
              @click="store.restartSimulation()"
              :disabled="store.isCalculating || isAnimating"
              class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white font-extrabold px-4 py-2 rounded-xl text-xs shadow-md transition-all flex items-center space-x-1.5"
              title="Ulangi simulasi rute dari awal"
            >
              <span>Ulangi Simulasi</span>
              <span>🔄</span>
            </button>
          </template>

          <!-- Advance Specific Courier or All (when not finished) -->
          <button
            v-else
            @click="$emit('advance-all')"
            :disabled="!store.canAdvanceAny || store.isCalculating || isAnimating"
            class="bg-primary hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed text-ink font-extrabold px-4 py-2 rounded-xl text-xs shadow-md transition-all flex items-center space-x-1"
            title="Lanjut 1 langkah untuk semua kurir aktif"
          >
            <span>Lanjut Semua</span>
            <span>⏩</span>
          </button>

          <label class="flex items-center gap-2 whitespace-nowrap text-xs font-bold text-slate-700" @click.stop>
            <span>Kecepatan</span>
            <input v-model.number="store.animationSpeed" type="range" min="0.5" max="5" step="0.5" class="w-20 accent-emerald-500">
            <span class="w-8 font-mono text-ink">{{ store.animationSpeed }}x</span>
          </label>
        </div>

        <!-- Action: Reset -->
        <button 
          @click="showResetConfirmation = true"
          :disabled="store.isCalculating || isAnimating"
          class="bg-white/70 hover:bg-white text-slate-600 hover:text-ink font-bold px-3 py-2 rounded-xl text-xs border border-line transition-all"
          title="Reset Sesi"
        >
          Reset
        </button>
      </div>
    </div>

    <Transition name="drawer-content">
    <div v-if="store.isBottomDrawerOpen" class="drawer-content flex-1 flex flex-col overflow-hidden bg-slate-50">
      <!-- Tabs Navigation -->
      <div class="flex border-b border-slate-200 bg-white px-6">
        <button 
          @click="store.bottomDrawerTab = 'packages'; store.clickMode = 'package'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'packages' ? 'border-primary text-primary bg-primary-soft' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Input Paket & Skenario</span>
          <span class="px-1.5 py-0.5 bg-slate-100 rounded text-[10px] text-slate-600 font-mono">{{ store.packages.length }}/50</span>
        </button>

        <button 
          @click="store.bottomDrawerTab = 'couriers'; store.clickMode = 'ref_point'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'couriers' ? 'border-primary text-primary bg-primary-soft' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>Kelola Kurir & Titik Acuan</span>
          <span class="px-1.5 py-0.5 bg-slate-100 rounded text-[10px] text-slate-600 font-mono">{{ store.couriers.length }}/10</span>
        </button>

        <button 
          @click="store.bottomDrawerTab = 'history'; store.clickMode = 'package'"
          class="py-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5"
          :class="store.bottomDrawerTab === 'history' ? 'border-primary text-primary bg-primary-soft' : 'border-transparent text-slate-500 hover:text-slate-800'"
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
              :disabled="store.couriers.length >= 10 || store.isRouteStarted"
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
              :class="store.activeCourierId === c.id ? 'border-primary ring-2 ring-primary-soft' : 'border-slate-200'"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-1.5">
                  <input 
                    type="color" 
                    v-model="c.color" 
                    :disabled="store.isRouteStarted || store.isCalculating"
                    class="w-6 h-6 rounded border-0 cursor-pointer" 
                    title="Pilih Warna Kurir"
                  />
                  <button
                    v-if="!store.isRouteStarted"
                    @click="store.randomizeCourierColor(c.id)"
                    type="button"
                    class="px-1.5 py-0.5 text-xs rounded hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors"
                    title="Acak Warna Kurir Ini"
                  >
                    🎲
                  </button>
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
                  class="text-slate-400 hover:text-red-500 text-xs font-bold"
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

              <!-- Adaptive Algorithm Info Badge -->
              <div v-if="store.courierStates[c.id]?.algorithmUsed" class="mt-2.5 bg-blue-50 border border-blue-200 rounded-xl p-2 text-[11px] text-blue-900 flex flex-col gap-0.5">
                <div class="flex items-center justify-between">
                  <span class="font-extrabold text-blue-700 flex items-center gap-1">
                    <span>⚡</span> {{ store.courierStates[c.id].algorithmUsed }}
                  </span>
                  <span class="font-mono text-slate-600 text-[10px]">
                    {{ store.courierStates[c.id].remainingPackageIds?.length }} sisa paket
                  </span>
                </div>
                <span class="text-[10px] text-slate-500 leading-tight">
                  {{ store.courierStates[c.id].reasoning }}
                </span>
              </div>

              <!-- Set Active Button -->
              <button 
                @click="store.activeCourierId = c.id; store.clickMode = 'ref_point'"
                :disabled="store.isRouteStarted || store.isCalculating"
                class="mt-3 w-full py-1.5 rounded-xl text-xs font-bold transition-all border"
                :class="store.activeCourierId === c.id 
                  ? 'bg-primary text-white border-primary shadow' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'"
              >
                {{ store.activeCourierId === c.id ? 'Sedang Dipilih (Klik Peta untuk Acuan)' : 'Pilih Kurir untuk Set Acuan' }}
              </button>
            </div>
          </div>
        </div>

        <!-- =================== TAB 3: HISTORY =================== -->
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
    </Transition>

    <div
      v-if="showResetConfirmation"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
      @click.self="showResetConfirmation = false"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="reset-dialog-title"
        aria-describedby="reset-dialog-description"
        class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl"
      >
        <h2 id="reset-dialog-title" class="text-base font-extrabold text-slate-900">Reset sesi?</h2>
        <p id="reset-dialog-description" class="mt-2 text-sm text-slate-600">
          Paket, kurir, hasil, dan riwayat akan dihapus. Apakah Anda yakin ingin mereset?
        </p>
        <div class="mt-6 flex justify-end gap-3">
          <button
            @click="showResetConfirmation = false"
            class="rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50"
          >
            Batalkan
          </button>
          <button
            @click="confirmReset"
            class="rounded-xl bg-red-600 px-4 py-2 text-xs font-bold text-white hover:bg-red-700"
          >
            Setuju, Reset
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'

defineProps({
  isAnimating: { type: Boolean, default: false }
})

defineEmits(['advance-all'])

const store = useAppStore()
const showResetConfirmation = ref(false)

function confirmReset() {
  showResetConfirmation.value = false
  store.resetSession()
}

function getCourierName(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.name : courierId
}

function getCourierColor(courierId) {
  const c = store.couriers.find(cr => cr.id === courierId)
  return c ? c.color : '#3B82F6'
}

</script>
