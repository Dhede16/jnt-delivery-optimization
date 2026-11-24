<template>
  <div class="relative w-full h-full">
    <!-- Leaflet Map Container -->
    <div ref="mapContainer" class="w-full h-full z-0 cursor-crosshair"></div>
    <!-- Active Map Feature -->
    <div v-if="!evaluationMode" class="map-mode-banner absolute top-4 left-4 z-10 flex items-center space-x-3 rounded-xl px-4 py-2 pointer-events-auto">
      <div class="flex items-center gap-2">
        <span class="h-3 w-3 rounded-full" :class="inputMode === 'package' ? 'bg-primary' : inputMode === 'move' ? 'bg-blue-500' : 'bg-amber-500'"></span>
        <div class="flex flex-col">
          <span class="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Fitur aktif</span>
          <span class="text-xs font-bold" :class="inputMode === 'package' ? 'text-primary' : inputMode === 'move' ? 'text-blue-600' : 'text-amber-600'">
            {{ inputMode === 'package' ? 'Tambah Paket' : inputMode === 'move' ? 'Pindahkan Lokasi' : `Titik Acuan — ${store.activeCourier?.name || 'Pilih Kurir'}` }}
          </span>
        </div>
      </div>
      <template v-if="store.isCalculating || store.isRouteStarted">
        <div class="h-7 w-px bg-slate-300"></div>
        <span class="text-[11px] font-medium text-slate-500">
          {{ store.isCalculating ? 'Menghitung alokasi & rute…' : 'Simulasi aktif' }}
        </span>
      </template>
    </div>

    <div v-if="!evaluationMode" role="toolbar" aria-label="Kontrol peta" class="absolute right-4 top-1/2 z-20 -translate-y-1/2">
      <div class="flex flex-col gap-1 rounded-2xl border border-white/80 bg-white/90 p-1.5 shadow-xl backdrop-blur-md">
        <div class="relative h-11 w-11">
          <button
            type="button"
            @click="inputMode = 'package'"
            :aria-pressed="inputMode === 'package'"
            aria-label="Tambah paket dengan klik peta"
            title="Tambah Paket"
            :disabled="store.isRouteStarted || store.isCalculating"
            class="flex h-11 w-11 items-center justify-center rounded-xl transition-colors disabled:cursor-not-allowed disabled:opacity-40"
            :class="inputMode === 'package' ? 'bg-primary text-white shadow-md' : 'text-slate-600 hover:bg-primary-soft hover:text-primary'"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
              <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" />
              <path d="m4.3 7.6 7.7 4.5 7.7-4.5M12 21v-9" />
              <path d="M16.5 12.5h5m-2.5-2.5v5" />
            </svg>
          </button>
          <button
            type="button"
            @click="toggleAddressSearch"
            :aria-expanded="isAddressSearchOpen"
            aria-label="Tambah paket dengan mencari alamat"
            title="Cari alamat paket"
            :disabled="store.isRouteStarted || store.isCalculating"
            class="!absolute !bottom-0 !right-0 !z-10 !h-5 !min-h-0 !w-5 flex items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 shadow-sm transition-colors hover:bg-primary-soft hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="h-3 w-3">
              <circle cx="10.5" cy="10.5" r="6.5" />
              <path d="m16 16 4 4" />
            </svg>
          </button>
        </div>
        <div class="relative h-11 w-11">
            <button
              type="button"
              @click="inputMode = 'reference'"
              :aria-pressed="inputMode === 'reference'"
              aria-label="Tambah titik acuan untuk kurir terpilih dengan klik peta"
              :title="`Titik Acuan${store.activeCourier ? ` — ${store.activeCourier.name}` : ''}`"
              :disabled="store.isRouteStarted || store.isCalculating"
              class="flex h-11 w-11 items-center justify-center rounded-xl transition-colors disabled:cursor-not-allowed disabled:opacity-40"
              :class="inputMode === 'reference' ? 'bg-primary text-white shadow-md' : 'text-slate-600 hover:bg-primary-soft hover:text-primary'"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
                <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
                <circle cx="12" cy="10" r="2.5" />
                <path d="M18 3v4m-2-2h4" />
              </svg>
            </button>
            <button
              type="button"
              @click="isCourierPickerOpen = !isCourierPickerOpen"
              :aria-expanded="isCourierPickerOpen"
              aria-label="Buka pilihan kurir untuk titik acuan"
              title="Pilih Kurir"
              :disabled="store.isRouteStarted || store.isCalculating"
              class="!absolute !bottom-0 !right-0 !z-10 !h-5 !min-h-0 !w-5 flex items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 shadow-sm transition-colors hover:bg-primary-soft hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3">
                <path :d="isCourierPickerOpen ? 'm10 18 6-6-6-6' : 'm14 18-6-6 6-6'" />
              </svg>
            </button>
        </div>
        <button
          type="button"
          @click="inputMode = 'move'"
          :aria-pressed="inputMode === 'move'"
          aria-label="Pindahkan paket, titik acuan, atau depot dengan menyeret marker"
          title="Pindahkan Lokasi"
          :disabled="store.isRouteStarted || store.isCalculating"
          class="flex h-11 w-11 items-center justify-center rounded-xl transition-colors disabled:cursor-not-allowed disabled:opacity-40"
          :class="inputMode === 'move' ? 'bg-primary text-white shadow-md' : 'text-slate-600 hover:bg-primary-soft hover:text-primary'"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
            <path d="M9 11V5a2 2 0 0 1 4 0v6-2a2 2 0 0 1 4 0v3-1a2 2 0 0 1 4 0v5a6 6 0 0 1-6 6h-1a6 6 0 0 1-5.2-3L5 15a2 2 0 0 1 3-2.6L9 14" />
          </svg>
        </button>
        <div class="mx-1 my-0.5 h-px bg-slate-200"></div>
        <button
          type="button"
          @click="map?.zoomIn()"
          aria-label="Perbesar peta"
          title="Zoom In"
          class="flex h-11 w-11 items-center justify-center rounded-xl text-slate-600 transition-colors hover:bg-primary-soft hover:text-primary"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="h-5 w-5">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
        <button
          type="button"
          @click="map?.zoomOut()"
          aria-label="Perkecil peta"
          title="Zoom Out"
          class="flex h-11 w-11 items-center justify-center rounded-xl text-slate-600 transition-colors hover:bg-primary-soft hover:text-primary"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="h-5 w-5">
            <path d="M5 12h14" />
          </svg>
        </button>
      </div>

      <div v-if="isAddressSearchOpen" role="search" aria-label="Cari alamat paket" class="absolute right-full top-0 mr-2 w-72 overflow-hidden rounded-2xl border border-white/80 bg-white/95 p-3 shadow-xl backdrop-blur-md">
        <h2 class="mb-2 text-xs font-extrabold text-slate-700">Tambah Paket dari Alamat</h2>
        <input
          v-model="addressQuery"
          type="search"
          autocomplete="off"
          aria-label="Cari alamat"
          placeholder="Ketik alamat atau nama tempat…"
          class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
        >
        <div class="mt-2 max-h-60 space-y-1 overflow-y-auto">
          <p v-if="addressQuery.trim().length < 3" class="px-2 py-2 text-[11px] text-slate-500"></p>
          <p v-else-if="isSearchingAddresses" role="status" class="px-2 py-2 text-[11px] text-slate-500">Mencari alamat…</p>
          <p v-else-if="addressSearchError" role="alert" class="px-2 py-2 text-[11px] text-red-600">{{ addressSearchError }}</p>
          <p v-else-if="addressSuggestions.length === 0" class="px-2 py-2 text-[11px] text-slate-500">Tidak ada saran alamat.</p>
          <button
            v-for="(feature, index) in addressSuggestions"
            :key="`${feature.properties?.osm_type}-${feature.properties?.osm_id}-${index}`"
            type="button"
            @click="addPackageFromAddress(feature)"
            :disabled="!store.canStartPackageInput || store.isRouteStarted || store.isCalculating || store.packages.length >= 50 || isAddingAddress"
            class="block w-full rounded-xl px-2.5 py-2 text-left text-xs text-slate-700 transition-colors hover:bg-primary-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            <span class="block font-semibold">{{ formatAddress(feature.properties) }}</span>
            <span class="mt-0.5 block text-[10px] text-slate-500">
              {{ feature.geometry.coordinates[1].toFixed(5) }}, {{ feature.geometry.coordinates[0].toFixed(5) }}
            </span>
          </button>
          <p v-if="!store.canStartPackageInput" class="px-2 py-2 text-[11px] text-amber-700">Tambahkan kurir dan titik acuan sebelum menambah paket.</p>
          <p v-else-if="store.packages.length >= 50" class="px-2 py-2 text-[11px] text-amber-700">Batas 50 paket sudah tercapai.</p>
        </div>
      </div>

      <div v-if="isCourierPickerOpen" class="absolute right-full top-1/2 mr-2 max-h-[70vh] w-52 -translate-y-1/2 overflow-y-auto rounded-2xl border border-white/80 bg-white/95 p-2 shadow-xl backdrop-blur-md">
        <h2 class="px-2 py-1.5 text-xs font-extrabold text-slate-700">Pilih Kurir</h2>
        <button
          v-for="courier in store.couriers"
          :key="courier.id"
          type="button"
          @click="selectCourier(courier.id)"
          :aria-pressed="store.activeCourierId === courier.id"
          :disabled="store.isRouteStarted || store.isCalculating"
          class="flex w-full items-center gap-2 rounded-xl border px-2.5 py-2 text-left transition-colors disabled:cursor-not-allowed disabled:opacity-40"
          :class="store.activeCourierId === courier.id ? 'border-primary bg-primary-soft' : 'border-transparent hover:bg-slate-50'"
        >
          <span class="h-3 w-3 shrink-0 rounded-full" :style="{ backgroundColor: courier.color }"></span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-xs font-bold text-slate-800">{{ courier.name }}</span>
            <span class="block text-[10px] text-slate-500">{{ courier.ref_points.length }} titik acuan</span>
          </span>
          <svg v-if="store.activeCourierId === courier.id" aria-hidden="true" viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4 shrink-0 text-primary">
            <path fill-rule="evenodd" d="M16.704 5.29a1 1 0 0 1 .006 1.414l-7.2 7.26a1 1 0 0 1-1.42.003L3.29 9.164a1 1 0 1 1 1.42-1.407l4.09 4.13 6.49-6.59a1 1 0 0 1 1.414-.006Z" clip-rule="evenodd" />
          </svg>
        </button>
        <div v-if="store.couriers.length === 0" class="px-2 py-2 text-[11px] text-slate-500">
          Belum ada kurir.
          <button
            type="button"
            class="ml-1 font-bold text-primary hover:underline"
            @click="store.bottomDrawerTab = 'couriers'; store.isBottomDrawerOpen = true"
          >
            Tambah Kurir
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Metrics (Paket & Kurir) Pojok Kanan Atas -->
    <div 
      v-if="!evaluationMode" 
      class="absolute top-4 right-14 z-10 flex items-center space-x-2 text-xs pointer-events-auto select-none"
    >
      <div class="flex items-center space-x-2 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-line shadow-sm">
        <span class="text-slate-400">Paket:</span>
        <span class="font-bold text-ink font-mono">{{ store.packages.length }}/50</span>
      </div>

      <div class="flex items-center space-x-2 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-line shadow-sm">
        <span class="text-slate-400">Kurir:</span>
        <span class="font-bold text-ink font-mono">{{ store.couriers.length }}/10</span>
      </div>
    </div>

    <!-- Fallback / Notice Alert -->
    <div
      v-if="!evaluationMode && store.isHaversineFallback && store.knnSteps.length"
      role="alert"
      class="absolute top-16 left-4 z-10 bg-amber-50/95 border border-amber-300 text-amber-800 px-3 py-1.5 rounded-lg shadow text-xs flex items-center space-x-2"
    >
      <span class="text-amber-500 font-bold">⚠️ Info Jarak:</span>
      <span>OSRM offline/limit. Menggunakan jarak garis lurus (Haversine).</span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import L from 'leaflet'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()
const props = defineProps({
  evaluationMode: { type: Boolean, default: false }
})
const mapContainer = ref(null)
const inputMode = ref('reference')
const isCourierPickerOpen = ref(false)
const isAddressSearchOpen = ref(false)
const addressQuery = ref('')
const addressSuggestions = ref([])
const addressSearchError = ref('')
const isSearchingAddresses = ref(false)
const isAddingAddress = ref(false)
const evaluationMethods = [
  { name: 'ACO' },
  { name: 'Nearest Neighbor' },
  { name: 'Dijkstra' },
  { name: 'Urutan Klik' }
]
let map = null

function selectCourier(courierId) {
  store.setActiveCourier(courierId)
  inputMode.value = 'reference'
  isCourierPickerOpen.value = false
  isAddressSearchOpen.value = false
  addressQuery.value = ''
}

function toggleAddressSearch() {
  isAddressSearchOpen.value = !isAddressSearchOpen.value
  isCourierPickerOpen.value = false
  inputMode.value = 'package'
  if (!isAddressSearchOpen.value) addressQuery.value = ''
}

function formatAddress(properties = {}) {
  const street = [properties?.housenumber, properties?.street].filter(Boolean).join(' ')
  return [
    properties?.name,
    street,
    properties?.district,
    properties?.city,
    properties?.state,
    properties?.country
  ].filter((part, index, parts) => part && parts.indexOf(part) === index).join(', ')
}

watch(addressQuery, (value, _, onCleanup) => {
  const query = value.trim()
  addressSuggestions.value = []
  addressSearchError.value = ''
  if (query.length < 3) {
    isSearchingAddresses.value = false
    return
  }

  isSearchingAddresses.value = true
  const controller = new AbortController()
  const timeout = setTimeout(async () => {
    try {
      const response = await axios.get('https://photon.komoot.io/api/', {
        params: {
          q: query,
          lat: store.depot.lat,
          lon: store.depot.lng,
          limit: 5
        },
        signal: controller.signal
      })
      addressSuggestions.value = (Array.isArray(response.data.features) ? response.data.features : [])
        .filter(feature => {
          const [lng, lat] = feature.geometry?.coordinates || []
          return Number.isFinite(lat) && Number.isFinite(lng) && Boolean(formatAddress(feature.properties))
        })
    } catch (error) {
      if (!controller.signal.aborted) {
        console.error('Address search failed:', error)
        addressSearchError.value = 'Pencarian alamat gagal. Coba lagi.'
      }
    } finally {
      if (!controller.signal.aborted) isSearchingAddresses.value = false
    }
  }, 350)

  onCleanup(() => {
    clearTimeout(timeout)
    controller.abort()
    isSearchingAddresses.value = false
  })
})

async function addPackageFromAddress(feature) {
  if (isAddingAddress.value) return
  const [lng, lat] = feature.geometry?.coordinates || []
  const name = formatAddress(feature.properties)
  if (!Number.isFinite(lat) || !Number.isFinite(lng) || !name) {
    addressSearchError.value = 'Data alamat tidak valid. Pilih saran lain.'
    return
  }

  const packageCount = store.packages.length
  isAddingAddress.value = true
  try {
    await store.addPackage(lat, lng, name)
    if (store.packages.length > packageCount) {
      map?.setView([lat, lng], Math.max(map.getZoom(), 15))
      isAddressSearchOpen.value = false
      addressQuery.value = ''
    } else if (store.errorMessage) {
      addressSearchError.value = store.errorMessage
    }
  } finally {
    isAddingAddress.value = false
  }
}

// Layers
let depotLayer = null
let refPointsLayer = null
let packagesLayer = null
let routePolylinesLayer = null
let evaluationLayer = null
let courierPositionLayer = null
const courierMarkers = new Map()
const plannedRouteLines = new Map()

onMounted(() => {
  initMap()
})

function initMap() {
  if (!mapContainer.value) return

  // Center around Samarinda Juanda
  map = L.map(mapContainer.value, {
    zoomControl: false
  }).setView([store.depot.lat, store.depot.lng], 13)

  if (props.evaluationMode) L.control.zoom({ position: 'topright' }).addTo(map)

  // OpenStreetMap Tile Layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors | J&T Samarinda'
  }).addTo(map)

  // Initialize Layer Groups
  depotLayer = L.layerGroup().addTo(map)
  refPointsLayer = L.layerGroup().addTo(map)
  packagesLayer = L.layerGroup().addTo(map)
  routePolylinesLayer = L.layerGroup().addTo(map)
  evaluationLayer = L.layerGroup().addTo(map)
  courierPositionLayer = L.layerGroup().addTo(map)

  // Map Click Listener
  map.on('click', (e) => {
    if (props.evaluationMode) return
    if (store.isRouteStarted || store.isCalculating) return
    if (inputMode.value === 'move') return
    const { lat, lng } = e.latlng

    if (inputMode.value === 'package') {
      store.addPackage(lat, lng)
      return
    }
    if (!store.activeCourierId) {
      store.errorMessage = 'Tambahkan dan pilih kurir di tab Kelola Kurir sebelum menambahkan titik acuan.'
      store.bottomDrawerTab = 'couriers'
      store.isBottomDrawerOpen = true
      return
    }
    store.addRefPoint(store.activeCourierId, lat, lng)
  })

  renderAll()
}

// Watchers to update map
watch(
  () => [
    store.packages,
    store.couriers,
    store.courierStates,
    store.depot,
    store.isRouteStarted,
    store.isCalculating,
    inputMode.value,
    store.activeCourierId
  ],
  () => {
    renderAll()
  },
  { deep: true }
)

function renderAll() {
  if (!map) return
  renderDepot()
  renderRefPoints()
  renderPackages()
  renderRoutes()
  renderCourierPositions()
}

function renderDepot() {
  depotLayer.clearLayers()
  const d = store.depot

  const depotIcon = L.divIcon({
    className: 'custom-depot-marker',
    html: `
      <div style="position: relative; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
        <div class="pulse-ring"></div>
        <div style="background: #2563EB; color: white; border: 2px solid white; border-radius: 10px; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(37,99,235,0.5);">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 8.35V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.35A2 2 0 0 1 3.26 6.5l8-3.2a2 2 0 0 1 1.48 0l8 3.2A2 2 0 0 1 22 8.35Z"/>
            <path d="M6 18h12"/>
            <path d="M6 14h12"/>
            <rect width="12" height="12" x="6" y="10"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  })

  const marker = L.marker([d.lat, d.lng], {
    icon: depotIcon,
    draggable: inputMode.value === 'move' && !store.isRouteStarted && !store.isCalculating
  })
    .bindPopup(`
      <div style="font-family: inherit; font-size: 12px; padding: 4px;">
        <strong style="color: #2563EB; font-size: 13px;">${d.name}</strong>
        <p style="margin: 4px 0 0; color: #475569;">Pusat Distribusi Utama J&T Samarinda</p>
        <p style="margin: 2px 0 0; font-size: 10px; color: #64748b;">${d.lat.toFixed(5)}, ${d.lng.toFixed(5)}</p>
      </div>
    `)
  if (marker.options.draggable) {
    marker.on('dragend', async (event) => {
      const { lat, lng } = event.target.getLatLng()
      await store.moveDepot(lat, lng)
    })
  }
  marker.addTo(depotLayer)
}

function renderRefPoints() {
  refPointsLayer.clearLayers()

  store.couriers.forEach((courier) => {
    courier.ref_points.forEach((rp, idx) => {
      const icon = L.divIcon({
        className: 'custom-ref-marker',
        html: `
          <div style="background: white; border: 2px solid ${courier.color}; color: ${courier.color}; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.25); font-size: 11px; font-weight: bold;">
            🎯
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      })

      const marker = L.marker([rp.lat, rp.lng], {
        icon,
        draggable: inputMode.value === 'move' && !store.isRouteStarted && !store.isCalculating
      })
        .bindPopup(`
          <div style="font-size: 12px; padding: 2px;">
            <div style="color: ${courier.color}; font-weight: bold;">${rp.name || 'Titik Acuan'}</div>
            <div style="font-size: 11px; color: #64748b;">Milik: ${courier.name}</div>
            <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">${rp.lat.toFixed(5)}, ${rp.lng.toFixed(5)}</div>
            ${!store.isRouteStarted && !store.isCalculating ? `
              <button onclick="window.__removeRefPoint('${courier.id}', '${rp.id}')" style="margin-top: 6px; background: #fee2e2; color: #dc2626; border: none; padding: 3px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;">
                Hapus Titik Acuan
              </button>
            ` : ''}
          </div>
        `)
      if (marker.options.draggable) {
        marker.on('dragend', async (event) => {
          const { lat, lng } = event.target.getLatLng()
          await store.moveRefPoint(courier.id, rp.id, lat, lng)
        })
      }
      marker.addTo(refPointsLayer)
    })
  })
}

function renderPackages() {
  packagesLayer.clearLayers()
  const courierMap = new Map(store.couriers.map(c => [c.id, c]))

  store.packages.forEach((pkg, index) => {
    const courier = pkg.courier_id ? courierMap.get(pkg.courier_id) : null
    const color = courier ? courier.color : '#475569'
    const label = pkg.order !== null && pkg.order !== undefined ? `${pkg.order}` : `${index + 1}`

    const isFinishedForCourier = courier && store.courierStates[courier.id]?.isFinished
    const isVisited = courier && store.courierStates[courier.id] && !store.courierStates[courier.id].remainingPackageIds.includes(pkg.id) && store.isRouteStarted

    const markerColor = isVisited ? '#94A3B8' : color

    const icon = L.divIcon({
      className: 'custom-package-marker',
      html: `
        <div style="background: ${markerColor}; color: white; border: 2px solid white; border-radius: 9999px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.3); font-weight: 800; font-size: 11px;">
          ${isVisited ? '✓' : label}
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    })

    const marker = L.marker([pkg.lat, pkg.lng], {
      icon,
      draggable: inputMode.value === 'move' && !store.isRouteStarted && !store.isCalculating
    })
      .bindPopup(`
        <div style="font-size: 12px; padding: 2px;">
          <div style="font-weight: bold; color: ${color};">${escapeHtml(pkg.name || pkg.id)}</div>
          <div style="font-size: 11px; color: #475569; margin-top: 2px;">
            Kurir: <strong>${courier ? courier.name : 'Belum dialokasikan'}</strong>
          </div>
          ${pkg.order ? `<div style="font-size: 11px; color: #0284c7;">Urutan Kunjungan ACO: #${pkg.order}</div>` : ''}
          <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">${pkg.lat.toFixed(5)}, ${pkg.lng.toFixed(5)}</div>
          ${!store.isRouteStarted ? `
            <button onclick="window.__removePackage('${pkg.id}')" style="margin-top: 6px; background: #fee2e2; color: #dc2626; border: none; padding: 3px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;">
              Hapus Paket
            </button>
          ` : ''}
        </div>
      `)
    if (marker.options.draggable) {
      marker.on('dragend', async (event) => {
        const { lat, lng } = event.target.getLatLng()
        await store.movePackage(pkg.id, lat, lng)
      })
    }
    marker.addTo(packagesLayer)
  })
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character])
}

function renderRoutes() {
  routePolylinesLayer.clearLayers()
  plannedRouteLines.clear()
  const courierMap = new Map(store.couriers.map(c => [c.id, c]))

  for (const [courierId, state] of Object.entries(store.courierStates)) {
    const courier = courierMap.get(courierId)
    const color = courier ? courier.color : '#3B82F6'

    // 1. Road already traveled
    if (state.visitedCoordinates && state.visitedCoordinates.length > 1) {
      L.polyline(state.visitedCoordinates, {
        color: '#94A3B8',
        weight: 3.5,
        dashArray: '6, 6',
        opacity: 0.8
      }).addTo(routePolylinesLayer)
    }

    // 2. Road still to travel
    if (state.geometry && state.geometry.coordinates) {
      // GeoJSON coordinates are [lon, lat] -> convert to [lat, lon] for Leaflet
      const latlngs = state.geometry.coordinates.map(coord => [coord[1], coord[0]])
      const line = L.polyline(latlngs, {
        color,
        weight: 4.5,
        opacity: 0.9,
        lineJoin: 'round'
      }).addTo(routePolylinesLayer)
      plannedRouteLines.set(courierId, line)
    }
  }
}

function renderCourierPositions() {
  const courierMap = new Map(store.couriers.map(c => [c.id, c]))
  const activeCourierIds = new Set(Object.keys(store.courierStates))

  for (const [courierId, marker] of courierMarkers) {
    if (!activeCourierIds.has(courierId)) {
      courierPositionLayer.removeLayer(marker)
      courierMarkers.delete(courierId)
    }
  }

  for (const [courierId, state] of Object.entries(store.courierStates)) {
    if (!state.currentPos) continue
    const courier = courierMap.get(courierId)
    const color = courier ? courier.color : '#3B82F6'

    let marker = courierMarkers.get(courierId)
    if (!marker) {
      const icon = L.divIcon({
        className: 'courier-pos-marker',
        html: `
          <div style="background: white; border: 3px solid ${color}; color: ${color}; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.35); font-size: 15px;">
            🛵
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      })
      marker = L.marker([state.currentPos.lat, state.currentPos.lng], { icon }).addTo(courierPositionLayer)
      courierMarkers.set(courierId, marker)
    } else {
      marker.setLatLng([state.currentPos.lat, state.currentPos.lng])
    }
    marker.setZIndexOffset(inputMode.value === 'move' ? -1000 : 0)
    marker.bindPopup(`
        <div style="font-size: 12px; font-weight: bold; color: ${color};">
          Posisi Saat Ini: ${courier?.name || courierId}
          <div style="font-size: 11px; font-weight: normal; color: #475569; margin-top: 3px;">
            Sisa Paket: ${state.remainingPackageIds.length} | Ditempuh: ${(state.traveledM / 1000).toFixed(2)} km
          </div>
        </div>
      `)
  }
}

function animateCourierStep(courierId) {
  const state = store.courierStates[courierId]
  const marker = courierMarkers.get(courierId)
  const packageId = state?.remainingPackageIds[0]
  const destination = store.packages.find(pkg => pkg.id === packageId)
  if (!state?.currentPos || !marker || !destination) return Promise.resolve()

  const roadCoordinates = state.geometry?.coordinates || []
  const nearestIndex = (point, fromIndex = 0) => roadCoordinates.slice(fromIndex).reduce((nearest, coordinate, index) => {
    const distance = (coordinate[0] - point.lng) ** 2 + (coordinate[1] - point.lat) ** 2
    return distance < nearest.distance ? { index: fromIndex + index, distance } : nearest
  }, { index: fromIndex, distance: Infinity }).index
  const startIndex = nearestIndex(state.currentPos)
  const endIndex = nearestIndex(destination, startIndex)
  const path = roadCoordinates.slice(startIndex, endIndex + 1).map(([lng, lat]) => L.latLng(lat, lng))
  if (path.length < 2) return Promise.resolve([])

  const lengths = [0]
  for (let i = 1; i < path.length; i++) lengths.push(lengths[i - 1] + path[i - 1].distanceTo(path[i]))
  const totalDistance = lengths[lengths.length - 1]
  const duration = Math.max(500, Math.min(10000, totalDistance / (350 * store.animationSpeed) * 1000))
  const traveledLine = L.polyline([], {
    color: '#94A3B8',
    weight: 3.5,
    dashArray: '6, 6',
    opacity: 0.8
  }).addTo(routePolylinesLayer)
  const plannedLine = plannedRouteLines.get(courierId)

  return new Promise(resolve => {
    let startedAt
    const move = (timestamp) => {
      startedAt ??= timestamp
      const progress = Math.min((timestamp - startedAt) / duration, 1)
      const distance = totalDistance * progress
      let segment = lengths.findIndex(length => length >= distance)
      if (segment < 1) segment = 1
      const segmentLength = lengths[segment] - lengths[segment - 1]
      const segmentProgress = segmentLength ? (distance - lengths[segment - 1]) / segmentLength : 1
      const from = path[segment - 1]
      const to = path[segment]
      const currentPosition = L.latLng(
        from.lat + (to.lat - from.lat) * segmentProgress,
        from.lng + (to.lng - from.lng) * segmentProgress
      )
      marker.setLatLng(currentPosition)
      traveledLine.setLatLngs([...path.slice(0, segment), currentPosition])
      if (plannedLine) {
        plannedLine.setLatLngs([
          currentPosition,
          ...roadCoordinates.slice(startIndex + segment).map(([lng, lat]) => [lat, lng])
        ])
      }
      if (progress < 1) requestAnimationFrame(move)
      else {
        marker.setLatLng([destination.lat, destination.lng])
        resolve(path.map(point => [point.lat, point.lng]))
      }
    }
    requestAnimationFrame(move)
  })
}

async function animateEvaluation(comparisons) {
  evaluationLayer.clearLayers()
  const routes = comparisons.flatMap(comparison => {
    const method = evaluationMethods.find(item => comparison.method.includes(item.name))
    return method ? (comparison.routes || []).map(route => ({
      route,
      courier: store.couriers.find(item => item.id === route.courier_id)
    })) : []
  })
  const paths = await Promise.all(routes.map(async ({ courier, route }) => {
    const points = route.package_ids
      .map(id => store.packages.find(pkg => pkg.id === id))
      .filter(Boolean)
    if (points.length === 0) return null

    const coordinates = [
      [store.depot.lat, store.depot.lng],
      ...points.map(point => [point.lat, point.lng])
    ]
    const geometryRes = await axios.post('/api/geometry', { coordinates })
    const roadCoordinates = geometryRes.data.geojson.coordinates
    const latlngs = roadCoordinates.map(([lng, lat]) => L.latLng(lat, lng))
    if (latlngs.length < 2) return null

    L.polyline(latlngs, {
      color: courier?.color || '#3B82F6',
      weight: 3,
      opacity: 0.35,
      dashArray: '7, 7',
      lineJoin: 'round'
    }).addTo(evaluationLayer)

    points.forEach((point, index) => {
      const icon = L.divIcon({
        className: 'evaluation-stop-marker',
        html: `<div style="background:white;color:${courier?.color || '#3B82F6'};border:2px solid ${courier?.color || '#3B82F6'};border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;box-shadow:0 2px 6px rgba(0,0,0,.3)">${index + 1}</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      })
      L.marker([point.lat, point.lng], { icon }).addTo(evaluationLayer)
    })

    const line = L.polyline([], {
      color: courier?.color || '#3B82F6',
      weight: 4,
      opacity: 0.8,
      lineJoin: 'round'
    }).addTo(evaluationLayer)

    const courierIndex = store.couriers.findIndex(item => item.id === route.courier_id)
    const icon = L.divIcon({
      className: 'evaluation-route-marker',
      html: `<div style="background:${courier?.color || '#3B82F6'};color:white;border:2px solid white;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;box-shadow:0 2px 6px rgba(0,0,0,.35)">${courierIndex + 1}</div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    })
    const marker = L.marker(latlngs[0], { icon }).addTo(evaluationLayer)
    return { latlngs, marker, line }
  }))
  const validPaths = paths.filter(Boolean)

  if (validPaths.length) {
    const bounds = L.latLngBounds(validPaths.flatMap(path => path.latlngs))
    map.fitBounds(bounds, { padding: [48, 48] })
  }
  await Promise.all(validPaths.map(({ latlngs, marker, line }) => animateEvaluationPath(latlngs, marker, line)))
}

function animateEvaluationPath(path, marker, line) {
  const lengths = [0]
  for (let i = 1; i < path.length; i++) {
    lengths.push(lengths[i - 1] + path[i - 1].distanceTo(path[i]))
  }
  const totalDistance = lengths[lengths.length - 1]
  if (!totalDistance) return Promise.resolve()

  return new Promise(resolve => {
    let elapsed = 0
    let previousTimestamp
    const move = timestamp => {
      if (previousTimestamp !== undefined) {
        elapsed += (timestamp - previousTimestamp) * store.animationSpeed
      }
      previousTimestamp = timestamp
      const progress = Math.min(elapsed / 6000, 1)
      const distance = totalDistance * progress
      let segment = lengths.findIndex(length => length >= distance)
      if (segment < 1) segment = 1
      const segmentLength = lengths[segment] - lengths[segment - 1]
      const segmentProgress = segmentLength ? (distance - lengths[segment - 1]) / segmentLength : 1
      const from = path[segment - 1]
      const to = path[segment]
      marker.setLatLng([
        from.lat + (to.lat - from.lat) * segmentProgress,
        from.lng + (to.lng - from.lng) * segmentProgress
      ])
      line.setLatLngs([...path.slice(0, segment), marker.getLatLng()])
      if (progress < 1) requestAnimationFrame(move)
      else {
        marker.setLatLng(path[path.length - 1])
        line.setLatLngs(path)
        resolve()
      }
    }
    requestAnimationFrame(move)
  })
}

defineExpose({ animateCourierStep, animateEvaluation })

// Global window helpers for leaflet popup buttons
window.__removePackage = (pkgId) => {
  store.removePackage(pkgId)
}
window.__removeRefPoint = (courierId, rpId) => {
  store.removeRefPoint(courierId, rpId)
}
</script>

<style scoped>
.package-loading-cursor {
  position: fixed;
  z-index: 1000;
  width: 22px;
  height: 22px;
  margin: 10px 0 0 10px;
  border: 3px solid #c7d2fe;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: package-loading-spin 0.7s linear infinite;
  pointer-events: none;
}

@keyframes package-loading-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
