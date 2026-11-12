<template>
  <div class="relative w-full h-full">
    <!-- Leaflet Map Container -->
    <div ref="mapContainer" class="w-full h-full z-0 cursor-crosshair"></div>
    <div
      v-if="isPackageLoading"
      class="package-loading-cursor"
      :style="{ left: `${cursorPosition.x}px`, top: `${cursorPosition.y}px` }"
      role="status"
      aria-label="Menghitung kurir dan rute paket"
    ></div>

    <!-- Mode Badge & Tooltip -->
    <div v-if="!evaluationMode" class="absolute top-4 left-20 z-10 bg-white/90 backdrop-blur-md px-4 py-2 rounded-xl shadow-lg border border-slate-200/80 flex items-center space-x-3 pointer-events-auto">
      <div class="flex items-center space-x-2">
        <span 
          class="w-3 h-3 rounded-full animate-pulse" 
          :class="store.clickMode === 'package' ? 'bg-indigo-600' : 'bg-amber-500'"
        ></span>
        <span class="text-xs font-semibold text-slate-700">
          Klik Peta: 
          <span class="text-indigo-600" v-if="store.clickMode === 'package'">
            {{ store.canStartPackageInput ? `Tambah Titik Paket (${store.packages.length}/50)` : 'Paket terkunci — atur kurir & acuan di panel bawah' }}
          </span>
          <span class="text-amber-600" v-else>Tambah Titik Acuan ({{ store.activeCourier?.name || 'Pilih Kurir' }})</span>
        </span>
      </div>
      <div class="h-4 w-px bg-slate-300"></div>
      <span class="text-[11px] text-slate-500">
        {{ store.isCalculating ? 'KNN dan ACO sedang dihitung…' : store.isRouteStarted ? '🔒 Simulasi aktif' : 'Klik di peta wilayah Samarinda' }}
      </span>
    </div>

    <!-- Fallback / Notice Alert -->
    <div
      v-if="!evaluationMode && store.isHaversineFallback && store.knnSteps.length"
      class="absolute top-16 left-20 z-10 bg-amber-50/95 border border-amber-300 text-amber-800 px-3 py-1.5 rounded-lg shadow text-xs flex items-center space-x-2"
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
const isPackageLoading = ref(false)
const cursorPosition = ref({ x: 0, y: 0 })
const evaluationMethods = [
  { name: 'ACO' },
  { name: 'Nearest Neighbor' },
  { name: 'Dijkstra' },
  { name: 'Urutan Klik' }
]
let map = null

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

  // Zoom control top right
  L.control.zoom({ position: 'topright' }).addTo(map)

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
    const { lat, lng } = e.latlng

    if (store.clickMode === 'ref_point') {
      if (!store.activeCourierId) {
        store.errorMessage = 'Tambahkan dan pilih kurir di tab Kelola Kurir sebelum menambahkan titik acuan.'
        store.bottomDrawerTab = 'couriers'
        store.isBottomDrawerOpen = true
        return
      }
      store.addRefPoint(store.activeCourierId, lat, lng)
    } else if (store.clickMode === 'package') {
      if (!store.addPackage(lat, lng)) return
      cursorPosition.value = { x: e.originalEvent.clientX, y: e.originalEvent.clientY }
      isPackageLoading.value = true
      store.calculateRoutes(false).finally(() => {
        isPackageLoading.value = false
      })
    }
  })

  map.on('mousemove', (e) => {
    if (isPackageLoading.value) {
      cursorPosition.value = { x: e.originalEvent.clientX, y: e.originalEvent.clientY }
    }
  })

  renderAll()
}

// Watchers to update map
watch(
  () => [
    store.packages,
    store.couriers,
    store.courierStates,
    store.isRouteStarted,
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
        <div style="background: #ED1C24; color: white; border: 2px solid white; border-radius: 10px; width: 34px; height: 34px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(237,28,36,0.5);">
          <span style="font-size: 10px; font-weight: 900; line-height: 1;">J&T</span>
          <span style="font-size: 7px; font-weight: 700; text-transform: uppercase;">Depot</span>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  })

  L.marker([d.lat, d.lng], { icon: depotIcon })
    .bindPopup(`
      <div style="font-family: inherit; font-size: 12px; padding: 4px;">
        <strong style="color: #ED1C24; font-size: 13px;">${d.name}</strong>
        <p style="margin: 4px 0 0; color: #475569;">Pusat Distribusi Utama J&T Samarinda</p>
        <p style="margin: 2px 0 0; font-size: 10px; color: #64748b;">${d.lat.toFixed(5)}, ${d.lng.toFixed(5)}</p>
      </div>
    `)
    .addTo(depotLayer)
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

      const marker = L.marker([rp.lat, rp.lng], { icon })
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

    const marker = L.marker([pkg.lat, pkg.lng], { icon })
      .bindPopup(`
        <div style="font-size: 12px; padding: 2px;">
          <div style="font-weight: bold; color: ${color};">${pkg.name || pkg.id}</div>
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
    marker.addTo(packagesLayer)
  })
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
