<template>
  <div class="relative w-screen h-screen overflow-hidden bg-slate-900 select-none">
    <!-- Top Alert Notifications -->
    <div 
      v-if="store.errorMessage" 
      class="fixed top-4 right-16 z-50 bg-red-600/95 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center space-x-3 text-xs font-semibold backdrop-blur-md border border-red-400"
    >
      <span>⚠️ {{ store.errorMessage }}</span>
      <button @click="store.errorMessage = ''" class="ml-2 font-bold hover:text-red-200">✕</button>
    </div>

    <div 
      v-if="store.warningMessage" 
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
    <AlgorithmExplorationPanel />

    <!-- Bottom Input & Controls Drawer -->
    <DataDrawer :is-animating="isAnimating" @advance-courier="advanceCourier" @advance-all="advanceAllCouriers" />

  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/appStore'
import MapView from './components/MapView.vue'
import AlgorithmExplorationPanel from './components/AlgorithmExplorationPanel.vue'
import DataDrawer from './components/DataDrawer.vue'

const store = useAppStore()
const mapView = ref(null)
const isAnimating = ref(false)

async function advanceCourier(courierId) {
  if (isAnimating.value) return
  isAnimating.value = true
  try {
    await mapView.value.animateCourierStep(courierId)
    await store.advanceCourierStep(courierId)
  } finally {
    isAnimating.value = false
  }
}

async function advanceAllCouriers() {
  if (isAnimating.value) return
  isAnimating.value = true
  try {
    const activeCourierIds = Object.entries(store.courierStates)
      .filter(([, state]) => !state.isFinished && state.remainingPackageIds.length > 0)
      .map(([courierId]) => courierId)
    await Promise.all(activeCourierIds.map(courierId => mapView.value.animateCourierStep(courierId)))
    await store.advanceAllCouriers()
  } finally {
    isAnimating.value = false
  }
}

onMounted(async () => {
  await store.init()
})
</script>
