import { defineStore } from 'pinia'
import axios from 'axios'

const DEFAULT_COLORS = [
  '#3B82F6', // Blue
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#F97316', // Orange
  '#6366F1', // Indigo
  '#14B8A6'  // Teal
]

export const useAppStore = defineStore('app', {
  state: () => ({
    depot: {
      id: 'depot-jnt',
      name: 'J&T Express Drop Point Juanda Samarinda',
      lat: -0.4897,
      lng: 117.1352
    },
    couriers: [],
    packages: [],
    activeCourierId: null,
    clickMode: 'package', // 'package' | 'ref_point'
    
    // Parameters
    knnParams: {
      k: 1,
      balanceLoad: false
    },
    acoParams: {
      alpha: 1.0,
      beta: 3.0,
      rho: 0.5,
      q: 100.0,
      iterations: 100
    },

    // Session Execution State
    isRouteStarted: false,
    isCalculating: false,
    animationSpeed: 1,
    errorMessage: '',
    warningMessage: '',
    
    // Matrix cache
    matrix: [],
    pointIds: [],
    isHaversineFallback: false,
    matrixSourceMessage: '',

    // Allocation & Steps
    allocations: {},
    knnSteps: [],
    knnRebalanceLogs: [],
    effectiveK: 3,

    // Courier Routing States: { [cid]: { currentPos, remainingPackageIds, currentTour, totalPlannedM, traveledM, geometry, isFinished, acoLogs, convergence } }
    courierStates: {},
    
    // History
    stepHistory: [],

    // Scenarios & Compare
    scenarios: [],
    comparisonData: null,

    // UI Panels
    isLeftPanelExpanded: false,
    isBottomDrawerOpen: true,
    bottomDrawerTab: 'packages', // 'packages' | 'couriers' | 'params' | 'scenarios' | 'history'
    activeAlgoTab: 'knn', // 'knn' | 'aco' | 'compare'
    selectedStepPackageId: null,
    selectedCourierForAco: 'c1'
  }),

  getters: {
    canCalculate(state) {
      if (state.isRouteStarted || state.isCalculating) return false
      if (state.couriers.length === 0 || state.packages.length === 0) return false
      return state.couriers.every(c => c.ref_points.length >= 1)
    },
    canStartPackageInput(state) {
      return state.couriers.length > 0 && state.couriers.every(c => c.ref_points.length >= 1)
    },
    canAdvanceAny(state) {
      if (!state.isRouteStarted || state.isCalculating) return false
      return Object.values(state.courierStates).some(cs => !cs.isFinished && cs.remainingPackageIds.length > 0)
    },
    allPackagesCount(state) {
      return state.packages.length
    },
    activeCourier(state) {
      return state.couriers.find(c => c.id === state.activeCourierId) || state.couriers[0] || null
    },
    totalRemainingPackages(state) {
      if (!state.isRouteStarted) return state.packages.length
      return Object.values(state.courierStates).reduce((sum, cs) => sum + cs.remainingPackageIds.length, 0)
    },
    totalDistancePlannedKm(state) {
      const meters = Object.values(state.courierStates).reduce((sum, cs) => sum + (cs.totalPlannedM || 0), 0)
      return (meters / 1000).toFixed(2)
    },
    totalDistanceTraveledKm(state) {
      const meters = Object.values(state.courierStates).reduce((sum, cs) => sum + (cs.traveledM || 0), 0)
      return (meters / 1000).toFixed(2)
    }
  },

  actions: {
    async init() {
      try {
        const [cfgRes, scnRes] = await Promise.all([
          axios.get('/api/config'),
          axios.get('/api/scenarios')
        ])
        if (cfgRes.data) {
          this.depot = cfgRes.data.depot
          this.knnParams.k = cfgRes.data.defaults.knn_k
          this.acoParams.alpha = cfgRes.data.defaults.aco_alpha
          this.acoParams.beta = cfgRes.data.defaults.aco_beta
          this.acoParams.rho = cfgRes.data.defaults.aco_rho
          this.acoParams.q = cfgRes.data.defaults.aco_q
          this.acoParams.iterations = cfgRes.data.defaults.aco_iterations
        }
        if (scnRes.data && scnRes.data.scenarios) {
          this.scenarios = scnRes.data.scenarios
        }
      } catch (err) {
        console.error('Init error:', err)
      }
    },

    setClickMode(mode) {
      this.clickMode = mode
    },

    setActiveCourier(courierId) {
      this.activeCourierId = courierId
    },

    async refreshPackageAllocation() {
      this.resetRoutingStateOnly()
      if (this.canCalculate) await this.calculateRoutes(false)
    },

    async addCourier(name = '') {
      if (this.isRouteStarted || this.isCalculating) return
      if (this.couriers.length >= 10) {
        alert('Maksimal 10 kurir diperbolehkan.')
        return
      }
      const idx = this.couriers.length
      const id = `c${Date.now()}-${this.couriers.length + 1}`
      const newCourier = {
        id,
        name: name || `Kurir ${String.fromCharCode(65 + idx)}`,
        color: DEFAULT_COLORS[idx % DEFAULT_COLORS.length],
        ref_points: []
      }
      this.couriers.push(newCourier)
      this.activeCourierId = id
      this.clickMode = 'ref_point'
      await this.refreshPackageAllocation()
    },

    async removeCourier(courierId) {
      if (this.isRouteStarted || this.isCalculating) return
      this.couriers = this.couriers.filter(c => c.id !== courierId)
      if (this.activeCourierId === courierId) this.activeCourierId = this.couriers[0]?.id || null
      await this.refreshPackageAllocation()
    },

    async addRefPoint(courierId, lat, lng, name = '') {
      if (this.isRouteStarted || this.isCalculating) return
      const courier = this.couriers.find(c => c.id === courierId)
      if (!courier) return
      const count = courier.ref_points.length + 1
      courier.ref_points.push({
        id: `ref-${courier.id}-${Date.now().toString().slice(-4)}`,
        name: name || `Acuan ${courier.name} #${count}`,
        lat: Number(lat.toFixed(5)),
        lng: Number(lng.toFixed(5))
      })
      await this.refreshPackageAllocation()
    },

    async removeRefPoint(courierId, refPointId) {
      if (this.isRouteStarted || this.isCalculating) return
      const courier = this.couriers.find(c => c.id === courierId)
      if (!courier) return
      courier.ref_points = courier.ref_points.filter(rp => rp.id !== refPointId)
      await this.refreshPackageAllocation()
    },

    addPackage(lat, lng, name = '') {
      if (this.isRouteStarted || this.isCalculating) return false
      if (!this.canStartPackageInput) {
        this.errorMessage = 'Tambahkan kurir dan minimal satu titik acuan untuk setiap kurir sebelum menyebar paket.'
        this.bottomDrawerTab = 'couriers'
        this.isBottomDrawerOpen = true
        this.clickMode = 'ref_point'
        return false
      }
      if (this.packages.length >= 50) {
        alert('Maksimal 50 paket. Titik ke-51 ditolak.')
        return false
      }
      const num = this.packages.length + 1
      const id = `P${String(num).padStart(2, '0')}`
      this.packages.push({
        id,
        name: name || `Paket #${num}`,
        lat: Number(lat.toFixed(5)),
        lng: Number(lng.toFixed(5)),
        courier_id: null,
        order: null
      })
      this.resetRoutingStateOnly()
      return true
    },

    async removePackage(pkgId) {
      if (this.isRouteStarted || this.isCalculating) return
      this.packages = this.packages.filter(p => p.id !== pkgId)
      this.resetRoutingStateOnly()
      if (this.packages.length > 0) await this.calculateRoutes(false)
    },

    async loadScenario(scenarioId) {
      if (this.isRouteStarted || this.isCalculating) return
      if (!this.canStartPackageInput) {
        this.errorMessage = 'Tambahkan kurir dan minimal satu titik acuan untuk setiap kurir sebelum memuat skenario.'
        this.bottomDrawerTab = 'couriers'
        return
      }
      const sc = this.scenarios.find(s => s.id === scenarioId)
      if (!sc) return
      this.packages = JSON.parse(JSON.stringify(sc.packages))
      this.resetRoutingStateOnly()
      await this.calculateRoutes(false)
    },

    resetRoutingStateOnly() {
      this.isRouteStarted = false
      this.allocations = {}
      this.knnSteps = []
      this.knnRebalanceLogs = []
      this.courierStates = {}
      this.stepHistory = []
      this.comparisonData = null
      this.packages.forEach(p => {
        p.courier_id = null
        p.order = null
      })
    },

    resetSession() {
      if (this.isCalculating) return
      this.isRouteStarted = false
      this.isCalculating = false
      this.isBottomDrawerOpen = true
      this.bottomDrawerTab = 'packages'
      this.packages = []
      this.couriers = []
      this.activeCourierId = null
      this.clickMode = 'package'
      this.errorMessage = ''
      this.warningMessage = ''
      this.allocations = {}
      this.knnSteps = []
      this.knnRebalanceLogs = []
      this.courierStates = {}
      this.stepHistory = []
      this.comparisonData = null
    },

    async calculateRoutes(startSimulation = true) {
      if (!this.canCalculate) return
      this.isCalculating = true
      this.errorMessage = ''
      this.warningMessage = ''

      try {
        // 1. Compute Matrix
        const matrixRes = await axios.post('/api/matrix', {
          depot: this.depot,
          packages: this.packages
        })
        this.matrix = matrixRes.data.matrix
        this.pointIds = matrixRes.data.point_ids
        this.isHaversineFallback = matrixRes.data.is_haversine_fallback
        this.matrixSourceMessage = matrixRes.data.source_message

        // 2. Compute KNN Allocation
        const allocRes = await axios.post('/api/allocate', {
          couriers: this.couriers,
          packages: this.packages,
          k: this.knnParams.k,
          balance_load: this.knnParams.balanceLoad
        })
        this.allocations = allocRes.data.allocations
        this.knnSteps = allocRes.data.steps
        this.knnRebalanceLogs = allocRes.data.rebalance_logs
        this.effectiveK = allocRes.data.effective_k
        if (allocRes.data.warning) {
          this.warningMessage = allocRes.data.warning
        }
        if (this.knnSteps.length > 0) {
          this.selectedStepPackageId = this.knnSteps[0].package_id
        }

        // Tag packages with winner courier
        const pkgMap = new Map(this.packages.map(p => [p.id, p]))
        for (const [cid, pkgIds] of Object.entries(this.allocations)) {
          pkgIds.forEach(pid => {
            const pkg = pkgMap.get(pid)
            if (pkg) pkg.courier_id = cid
          })
        }

        // 3. For each courier with packages, run ACO TSP from depot
        const newCourierStates = {}

        for (const courier of this.couriers) {
          const assignedPkgIds = this.allocations[courier.id] || []
          if (assignedPkgIds.length === 0) {
            newCourierStates[courier.id] = {
              currentPos: { lat: this.depot.lat, lng: this.depot.lng },
              remainingPackageIds: [],
              currentTour: [],
              totalPlannedM: 0,
              traveledM: 0,
              geometry: null,
              visitedCoordinates: [],
              isFinished: true,
              acoLogs: [],
              convergence: []
            }
            continue
          }

          const optRes = await axios.post('/api/optimize', {
            courier_id: courier.id,
            matrix: this.matrix,
            point_ids: this.pointIds,
            start_id: this.depot.id,
            package_ids: assignedPkgIds,
            alpha: this.acoParams.alpha,
            beta: this.acoParams.beta,
            rho: this.acoParams.rho,
            q: this.acoParams.q,
            iterations: this.acoParams.iterations
          })

          const tour = optRes.data.tour // List of package ids in visit order
          // Assign order numbers to packages
          tour.forEach((pid, idx) => {
            const pkg = pkgMap.get(pid)
            if (pkg) pkg.order = idx + 1
          })

          // Calculate road geometry: depot -> tour stops
          const waypoints = [
            [this.depot.lat, this.depot.lng],
            ...tour.map(pid => {
              const p = pkgMap.get(pid)
              return [p.lat, p.lng]
            })
          ]
          const geomRes = await axios.post('/api/geometry', { coordinates: waypoints })

          newCourierStates[courier.id] = {
            currentPos: { lat: this.depot.lat, lng: this.depot.lng },
            remainingPackageIds: [...tour],
            currentTour: [...tour],
            totalPlannedM: optRes.data.total_distance_m,
            traveledM: 0,
            geometry: geomRes.data.geojson,
            visitedCoordinates: [[this.depot.lat, this.depot.lng]],
            isFinished: false,
            acoLogs: optRes.data.iterations_log,
            convergence: optRes.data.convergence
          }
        }

        this.courierStates = newCourierStates
        this.isRouteStarted = startSimulation
        if (startSimulation) this.isBottomDrawerOpen = false
        this.selectedCourierForAco = this.couriers.find(c => (this.allocations[c.id] || []).length > 0)?.id || this.couriers[0].id
      } catch (err) {
        console.error('Error during calculateRoutes:', err)
        this.errorMessage = err.response?.data?.detail || err.message || 'Terjadi kesalahan perhitungan rute.'
      } finally {
        this.isCalculating = false
      }
    },

    async advanceCourierStep(courierId, traveledCoordinates = []) {
      const cs = this.courierStates[courierId]
      const courier = this.couriers.find(c => c.id === courierId)
      if (!cs || cs.isFinished || cs.remainingPackageIds.length === 0) return

      const pkgMap = new Map(this.packages.map(p => [p.id, p]))
      const nextPkgId = cs.remainingPackageIds[0]
      const nextPkg = pkgMap.get(nextPkgId)
      if (!nextPkg) return

      // Measure segment distance from currentPos to nextPkg
      const idToIdx = new Map(this.pointIds.map((id, idx) => [id, idx]))
      const fromIdx = (cs.currentTour.indexOf(nextPkgId) === 0 && cs.traveledM === 0)
        ? idToIdx.get(this.depot.id)
        : idToIdx.get(cs.currentTour[cs.currentTour.indexOf(nextPkgId) - 1])
      const toIdx = idToIdx.get(nextPkgId)

      let segDistM = 0
      if (fromIdx !== undefined && toIdx !== undefined && this.matrix[fromIdx]) {
        segDistM = this.matrix[fromIdx][toIdx]
      }

      cs.traveledM += segDistM
      cs.currentPos = { lat: nextPkg.lat, lng: nextPkg.lng }
      cs.visitedCoordinates.push(...traveledCoordinates.slice(1))

      // Record History
      const stepNumber = this.stepHistory.filter(h => h.courierId === courierId).length + 1
      const fromName = stepNumber === 1 ? 'Depot Juanda' : `Paket #${this.stepHistory.filter(h => h.courierId === courierId).slice(-1)[0]?.toName || 'Sebelumnya'}`
      this.stepHistory.push({
        courierId,
        courierName: courier.name,
        courierColor: courier.color,
        stepIndex: stepNumber,
        fromName,
        toName: nextPkg.name || nextPkg.id,
        distanceKm: (segDistM / 1000).toFixed(3),
        cumulativeKm: (cs.traveledM / 1000).toFixed(3),
        remainingCount: cs.remainingPackageIds.length - 1
      })

      // Remove visited package
      cs.remainingPackageIds.shift()

      if (cs.remainingPackageIds.length === 0) {
        cs.isFinished = true
        cs.geometry = null
        return
      }

      // Re-run ACO for remaining packages from current courier position
      try {
        const optRes = await axios.post('/api/optimize', {
          courier_id: courierId,
          matrix: this.matrix,
          point_ids: this.pointIds,
          start_id: nextPkgId,
          package_ids: cs.remainingPackageIds,
          alpha: this.acoParams.alpha,
          beta: this.acoParams.beta,
          rho: this.acoParams.rho,
          q: this.acoParams.q,
          iterations: this.acoParams.iterations
        })

        cs.remainingPackageIds = [...optRes.data.tour]
        cs.acoLogs = optRes.data.iterations_log
        cs.convergence = optRes.data.convergence

        // Update remaining road geometry
        const waypoints = [
          [cs.currentPos.lat, cs.currentPos.lng],
          ...cs.remainingPackageIds.map(pid => {
            const p = pkgMap.get(pid)
            return [p.lat, p.lng]
          })
        ]
        const geomRes = await axios.post('/api/geometry', { coordinates: waypoints })
        cs.geometry = geomRes.data.geojson
      } catch (err) {
        console.error('Error re-optimizing courier remaining stops:', err)
      }
    },

    async advanceAllCouriers(traveledCoordinates = {}) {
      const activeCourierIds = Object.keys(this.courierStates).filter(cid => {
        const cs = this.courierStates[cid]
        return cs && !cs.isFinished && cs.remainingPackageIds.length > 0
      })
      for (const cid of activeCourierIds) {
        await this.advanceCourierStep(cid, traveledCoordinates[cid])
      }
    },

    async runComparison() {
      if (this.packages.length === 0 || this.couriers.length === 0) return
      this.isCalculating = true
      try {
        let m = this.matrix
        let pids = this.pointIds
        if (!m || m.length === 0) {
          const matrixRes = await axios.post('/api/matrix', {
            depot: this.depot,
            packages: this.packages
          })
          m = matrixRes.data.matrix
          pids = matrixRes.data.point_ids
        }
        const res = await axios.post('/api/compare', {
          couriers: this.couriers,
          packages: this.packages,
          depot: this.depot,
          matrix: m,
          point_ids: pids,
          k: this.knnParams.k,
          balance_load: this.knnParams.balanceLoad,
          alpha: this.acoParams.alpha,
          beta: this.acoParams.beta,
          rho: this.acoParams.rho,
          q: this.acoParams.q,
          iterations: this.acoParams.iterations
        })
        this.comparisonData = res.data
        this.activeAlgoTab = 'compare'
        this.isLeftPanelExpanded = true
      } catch (err) {
        console.error('Error running comparisons:', err)
      } finally {
        this.isCalculating = false
      }
    }
  }
})
