<template>
  <div class="app-shell relative w-screen h-screen overflow-hidden select-none">
    <template v-if="isEvaluationWindow">
      <MapView ref="mapView" evaluation-mode />
      <div class="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-3 rounded-xl bg-white/95 p-3 shadow-xl">
        <strong class="text-sm text-slate-800">Simulasi {{ evaluationMethod?.name }}</strong>
        <span v-if="isEvaluationLoading" class="text-xs font-semibold text-indigo-700">Menghitung metode dan menyiapkan rute...</span>
        <label class="flex items-center gap-2 text-xs font-bold text-slate-700">
          Kecepatan
          <input v-model.number="store.animationSpeed" type="range" min="0.5" max="5" step="0.5" class="w-24 accent-indigo-600">
          <span class="w-8 font-mono">{{ store.animationSpeed }}x</span>
        </label>
        <button
          @click="startEvaluation(evaluationData?.routing_comparison)"
          :disabled="isAnimating || isEvaluationLoading || !evaluationData?.routing_comparison"
          class="rounded-lg bg-indigo-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-40"
        >
          {{ isAnimating ? 'Simulasi Berjalan...' : 'Ulangi Simulasi' }}
        </button>
      </div>
      <div class="absolute bottom-4 left-4 z-20 rounded-xl bg-white/95 p-3 shadow-xl text-xs font-semibold text-slate-700 space-y-1">
        <div v-if="evaluationMethod" class="font-bold">{{ evaluationMethod.name }}</div>
        <div
          v-for="courier in store.couriers.filter(item => evaluationData?.routing_comparison?.routes?.some(route => route.courier_id === item.id))"
          :key="courier.id"
          class="flex items-center gap-2"
        >
          <span class="h-1 w-4 rounded" :style="{ backgroundColor: courier.color }"></span>{{ courier.name }}
        </div>
      </div>
      <div v-if="evaluationError" class="absolute bottom-4 right-4 z-20 max-w-lg rounded-xl bg-red-600 p-3 text-xs font-semibold text-white shadow-xl">
        {{ evaluationError }}
      </div>
    </template>
    <template v-else>
    <!-- Top Alert Notifications -->
    <div 
      v-if="store.errorMessage"
      role="alert"
      class="fixed top-4 right-16 z-50 bg-red-600/95 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center space-x-3 text-xs font-semibold backdrop-blur-md border border-red-400"
    >
      <span>⚠️ {{ store.errorMessage }}</span>
      <button @click="store.errorMessage = ''" class="ml-2 font-bold hover:text-red-200">✕</button>
    </div>

    <div 
      v-if="store.warningMessage"
      role="alert"
      class="fixed top-4 right-16 z-50 bg-amber-500/95 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center space-x-3 text-xs font-semibold backdrop-blur-md border border-amber-300"
    >
      <span>ℹ️ {{ store.warningMessage }}</span>
      <button @click="store.warningMessage = ''" class="ml-2 font-bold hover:text-amber-200">✕</button>
    </div>

    <!-- Main Interactive Map Area -->
    <main class="w-full h-full">
      <MapView ref="mapView" />
    </main>

    <!-- Left Algorithm & Step-by-Step Transparency Panel -->
    <AlgorithmExplorationPanel @start-evaluation="openEvaluationWindow" />

    <!-- Bottom Input & Controls Drawer -->
    <DataDrawer :is-animating="isAnimating" @advance-all="advanceAllCouriers" />
    </template>

  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useAppStore } from './stores/appStore'
import MapView from './components/MapView.vue'
import AlgorithmExplorationPanel from './components/AlgorithmExplorationPanel.vue'
import DataDrawer from './components/DataDrawer.vue'

const store = useAppStore()
const mapView = ref(null)
const isAnimating = ref(false)
const isEvaluationWindow = new URLSearchParams(window.location.search).has('evaluation')
const evaluationMethods = [
  { name: 'ACO' },
  { name: 'Nearest Neighbor' },
  { name: 'Dijkstra' },
  { name: 'Urutan Klik' }
]
const evaluationData = ref(null)
const evaluationError = ref('')
const evaluationMethod = ref(null)
const isEvaluationLoading = ref(false)

async function advanceAllCouriers() {
  if (isAnimating.value) return
  isAnimating.value = true
  try {
    const activeCourierIds = Object.entries(store.courierStates)
      .filter(([, state]) => !state.isFinished && state.remainingPackageIds.length > 0)
      .map(([courierId]) => courierId)
    const traveledCoordinates = await Promise.all(activeCourierIds.map(
      async courierId => [courierId, await mapView.value.animateCourierStep(courierId)]
    ))
    await store.advanceAllCouriers(Object.fromEntries(traveledCoordinates))
  } finally {
    isAnimating.value = false
  }
}

function openEvaluationWindow(comparison) {
  if (!comparison?.routes?.length) return
  const token = `${Date.now()}-${Math.random().toString(36).slice(2)}`
  localStorage.setItem(`jnt-evaluation-${token}`, JSON.stringify({
    depot: store.depot,
    packages: store.packages,
    couriers: store.couriers,
    knnParams: store.knnParams,
    acoParams: store.acoParams,
    method: comparison.method,
    animationSpeed: store.animationSpeed
  }))
  const url = new URL(window.location.href)
  url.searchParams.set('evaluation', token)
  const evaluationWindow = window.open(url.toString(), '_blank')
  if (!evaluationWindow) {
    localStorage.removeItem(`jnt-evaluation-${token}`)
    store.errorMessage = 'Browser memblokir tab baru. Izinkan pop-up lalu coba lagi.'
    return
  }
  evaluationWindow.opener = null
}

async function startEvaluation(comparison) {
  if (isAnimating.value || !comparison?.routes?.length || !mapView.value) return
  isAnimating.value = true
  evaluationError.value = ''
  try {
    await mapView.value.animateEvaluation([comparison])
  } catch (err) {
    console.error('Error during evaluation simulation:', err)
    evaluationError.value = err.response?.data?.detail || err.message || 'Gagal menampilkan rute evaluasi.'
  } finally {
    isAnimating.value = false
  }
}

onMounted(async () => {
  if (isEvaluationWindow) {
    try {
      const token = new URLSearchParams(window.location.search).get('evaluation')
      const rawData = localStorage.getItem(`jnt-evaluation-${token}`)
      if (!rawData) throw new Error('Data simulasi tidak ditemukan. Buka simulasi dari halaman evaluasi utama.')
      localStorage.removeItem(`jnt-evaluation-${token}`)
      evaluationData.value = JSON.parse(rawData)
      store.depot = evaluationData.value.depot
      store.packages = evaluationData.value.packages
      store.couriers = evaluationData.value.couriers
      store.knnParams = evaluationData.value.knnParams
      store.acoParams = evaluationData.value.acoParams
      store.animationSpeed = evaluationData.value.animationSpeed || 1
      evaluationMethod.value = evaluationMethods.find(method =>
        evaluationData.value.method.includes(method.name)
      )
      if (!evaluationMethod.value) throw new Error('Metode simulasi tidak dikenali.')
      await nextTick()
      isEvaluationLoading.value = true
      const results = await store.runComparison()
      if (!results) throw new Error(store.errorMessage || 'Evaluasi metode gagal dihitung.')
      evaluationData.value.routing_comparison = results.routing_comparisons.find(
        comparison => comparison.method === evaluationData.value.method
      )
      if (!evaluationData.value.routing_comparison) throw new Error('Hasil untuk metode ini tidak ditemukan.')
      isEvaluationLoading.value = false
      await startEvaluation(evaluationData.value.routing_comparison)
    } catch (err) {
      evaluationError.value = err.message || 'Gagal memuat data simulasi.'
    } finally {
      isEvaluationLoading.value = false
    }
    return
  }
  await store.init()
})
</script>
