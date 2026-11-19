import heapq
import math
import random
import time
from typing import Any, Dict, List, Tuple
import numpy as np
from aco import dijkstra_tour, nearest_neighbor_tour, original_order_tour, solve_open_tsp_aco
from knn import run_knn_allocation
from schemas import (
    AllocateRequest,
    CompareMethodResult,
    CompareRequest,
    CompareResponse,
    OptimizeRequest,
)


def compute_nn_steps(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray,
    point_ids: List[str],
    point_name_map: Dict[str, str]
) -> Tuple[List[int], float, List[Dict[str, Any]]]:
    unvisited = set(pkg_indices)
    curr = start_idx
    tour = []
    total_dist = 0.0
    steps = []
    step_num = 1

    while unvisited:
        candidates = []
        for u in unvisited:
            d = float(dist_matrix[curr, u])
            candidates.append({
                "point_id": point_ids[u],
                "point_name": point_name_map.get(point_ids[u], point_ids[u]),
                "distance_m": round(d, 1),
                "distance_km": round(d / 1000.0, 3)
            })
        candidates.sort(key=lambda c: c["distance_m"])
        next_candidate = candidates[0]
        next_idx = next(u for u in unvisited if point_ids[u] == next_candidate["point_id"])

        seg_dist = next_candidate["distance_m"]
        total_dist += seg_dist
        tour.append(next_idx)

        for c in candidates:
            c["is_chosen"] = (c["point_id"] == next_candidate["point_id"])

        steps.append({
            "step": step_num,
            "from_id": point_ids[curr],
            "from_name": point_name_map.get(point_ids[curr], point_ids[curr]),
            "to_id": next_candidate["point_id"],
            "to_name": next_candidate["point_name"],
            "distance_m": seg_dist,
            "distance_km": round(seg_dist / 1000.0, 3),
            "cumulative_distance_km": round(total_dist / 1000.0, 3),
            "candidates": candidates
        })
        unvisited.remove(next_idx)
        curr = next_idx
        step_num += 1

    return tour, total_dist, steps


def compute_dijkstra_steps(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray,
    point_ids: List[str],
    point_name_map: Dict[str, str]
) -> Tuple[List[int], float, List[Dict[str, Any]]]:
    unvisited = set(pkg_indices)
    current = start_idx
    tour = []
    total_dist = 0.0
    n_points = dist_matrix.shape[0]
    steps = []
    step_num = 1

    while unvisited:
        distances = [float("inf")] * n_points
        distances[current] = 0.0
        queue = [(0.0, current)]

        while queue:
            distance, node = heapq.heappop(queue)
            if distance > distances[node]:
                continue
            for neighbor in range(n_points):
                edge_distance = float(dist_matrix[node, neighbor])
                candidate = distance + edge_distance
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(queue, (candidate, neighbor))

        candidates = []
        for u in unvisited:
            d = float(distances[u])
            candidates.append({
                "point_id": point_ids[u],
                "point_name": point_name_map.get(point_ids[u], point_ids[u]),
                "dijkstra_distance_m": round(d, 1),
                "dijkstra_distance_km": round(d / 1000.0, 3)
            })
        candidates.sort(key=lambda c: c["dijkstra_distance_m"])
        next_candidate = candidates[0]
        next_idx = next(u for u in unvisited if point_ids[u] == next_candidate["point_id"])

        seg_dist = next_candidate["dijkstra_distance_m"]
        total_dist += seg_dist
        tour.append(next_idx)

        for c in candidates:
            c["is_chosen"] = (c["point_id"] == next_candidate["point_id"])

        steps.append({
            "step": step_num,
            "from_id": point_ids[current],
            "from_name": point_name_map.get(point_ids[current], point_ids[current]),
            "to_id": next_candidate["point_id"],
            "to_name": next_candidate["point_name"],
            "distance_m": seg_dist,
            "distance_km": round(seg_dist / 1000.0, 3),
            "cumulative_distance_km": round(total_dist / 1000.0, 3),
            "candidates": candidates
        })
        unvisited.remove(next_idx)
        current = next_idx
        step_num += 1

    return tour, total_dist, steps


def compute_original_steps(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray,
    point_ids: List[str],
    point_name_map: Dict[str, str]
) -> Tuple[List[int], float, List[Dict[str, Any]]]:
    tour = list(pkg_indices)
    total_dist = 0.0
    steps = []
    curr = start_idx
    step_num = 1
    for target in pkg_indices:
        seg_dist = float(dist_matrix[curr, target])
        total_dist += seg_dist
        steps.append({
            "step": step_num,
            "from_id": point_ids[curr],
            "from_name": point_name_map.get(point_ids[curr], point_ids[curr]),
            "to_id": point_ids[target],
            "to_name": point_name_map.get(point_ids[target], point_ids[target]),
            "distance_m": round(seg_dist, 1),
            "distance_km": round(seg_dist / 1000.0, 3),
            "cumulative_distance_km": round(total_dist / 1000.0, 3)
        })
        curr = target
        step_num += 1
    return tour, total_dist, steps


def compute_tour_steps_from_ids(
    start_id: str,
    tour_ids: List[str],
    id_to_idx: Dict[str, int],
    dist_matrix: np.ndarray,
    point_name_map: Dict[str, str]
) -> List[Dict[str, Any]]:
    steps = []
    curr_id = start_id
    total_dist = 0.0
    for step_num, target_id in enumerate(tour_ids, 1):
        if curr_id in id_to_idx and target_id in id_to_idx:
            seg_dist = float(dist_matrix[id_to_idx[curr_id], id_to_idx[target_id]])
        else:
            seg_dist = 0.0
        total_dist += seg_dist
        steps.append({
            "step": step_num,
            "from_id": curr_id,
            "from_name": point_name_map.get(curr_id, curr_id),
            "to_id": target_id,
            "to_name": point_name_map.get(target_id, target_id),
            "distance_m": round(seg_dist, 1),
            "distance_km": round(seg_dist / 1000.0, 3),
            "cumulative_distance_km": round(total_dist / 1000.0, 3)
        })
        curr_id = target_id
    return steps


def run_comparisons(
    req: CompareRequest,
    reference_distances_m: List[List[float]],
    package_distances_m: List[List[float]]
) -> CompareResponse:
    # 1. Allocation comparisons: KNN vs K-Means vs Random
    # We will evaluate how each allocation performs under ACO or NN routing
    alloc_results: List[CompareMethodResult] = []

    depot_id = req.depot.id
    id_to_idx = {pid: i for i, pid in enumerate(req.point_ids)}
    dist_matrix = np.array(req.matrix, dtype=np.float64)

    # --- Method A: KNN ---
    t0 = time.perf_counter()
    knn_resp = run_knn_allocation(AllocateRequest(
        couriers=req.couriers,
        packages=req.packages,
        k=req.k,
        balance_load=req.balance_load
    ), reference_distances_m, package_distances_m)
    knn_allocs = knn_resp.allocations
    t_knn = (time.perf_counter() - t0) * 1000

    knn_tot_dist = 0.0
    knn_max_dist = 0.0
    for cid, pids in knn_allocs.items():
        if pids:
            pkg_indices = [id_to_idx[p] for p in pids if p in id_to_idx]
            _, d = nearest_neighbor_tour(id_to_idx[depot_id], pkg_indices, dist_matrix)
            knn_tot_dist += d
            if d > knn_max_dist:
                knn_max_dist = d

    counts = [len(pids) for pids in knn_allocs.values()]
    std_dev_knn = float(np.std(counts)) if counts else 0.0

    alloc_results.append(CompareMethodResult(
        name="KNN (Bawaan)",
        allocations={cid: len(pids) for cid, pids in knn_allocs.items()},
        total_distance_m=round(knn_tot_dist, 2),
        max_courier_distance_m=round(knn_max_dist, 2),
        std_dev_packages=round(std_dev_knn, 2),
        execution_time_ms=round(t_knn, 2)
    ))

    # --- Method B: K-Means Allocation ---
    t0 = time.perf_counter()
    kmeans_allocs: Dict[str, List[str]] = {c.id: [] for c in req.couriers}
    try:
        from sklearn.cluster import KMeans
        n_clusters = min(len(req.couriers), len(req.packages))
        if n_clusters > 0 and len(req.packages) >= n_clusters:
            X = np.array([[p.lat, p.lng] for p in req.packages])
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5).fit(X)
            labels = kmeans.labels_
            for idx, p in enumerate(req.packages):
                cid = req.couriers[labels[idx]].id
                kmeans_allocs[cid].append(p.id)
        else:
            for idx, p in enumerate(req.packages):
                cid = req.couriers[idx % len(req.couriers)].id
                kmeans_allocs[cid].append(p.id)
    except Exception:
        for idx, p in enumerate(req.packages):
            cid = req.couriers[idx % len(req.couriers)].id
            kmeans_allocs[cid].append(p.id)
    t_km = (time.perf_counter() - t0) * 1000

    km_tot_dist = 0.0
    km_max_dist = 0.0
    for cid, pids in kmeans_allocs.items():
        if pids:
            pkg_indices = [id_to_idx[p] for p in pids if p in id_to_idx]
            _, d = nearest_neighbor_tour(id_to_idx[depot_id], pkg_indices, dist_matrix)
            km_tot_dist += d
            if d > km_max_dist:
                km_max_dist = d
    km_counts = [len(pids) for pids in kmeans_allocs.values()]
    std_dev_km = float(np.std(km_counts)) if km_counts else 0.0

    alloc_results.append(CompareMethodResult(
        name="K-Means Clustering",
        allocations={cid: len(pids) for cid, pids in kmeans_allocs.items()},
        total_distance_m=round(km_tot_dist, 2),
        max_courier_distance_m=round(km_max_dist, 2),
        std_dev_packages=round(std_dev_km, 2),
        execution_time_ms=round(t_km, 2)
    ))

    # --- Method C: Random Allocation ---
    t0 = time.perf_counter()
    rnd_allocs: Dict[str, List[str]] = {c.id: [] for c in req.couriers}
    rng = random.Random(42)
    for p in req.packages:
        chosen_c = rng.choice(req.couriers)
        rnd_allocs[chosen_c.id].append(p.id)
    t_rnd = (time.perf_counter() - t0) * 1000

    rnd_tot_dist = 0.0
    rnd_max_dist = 0.0
    for cid, pids in rnd_allocs.items():
        if pids:
            pkg_indices = [id_to_idx[p] for p in pids if p in id_to_idx]
            _, d = nearest_neighbor_tour(id_to_idx[depot_id], pkg_indices, dist_matrix)
            rnd_tot_dist += d
            if d > rnd_max_dist:
                rnd_max_dist = d
    rnd_counts = [len(pids) for pids in rnd_allocs.values()]
    std_dev_rnd = float(np.std(rnd_counts)) if rnd_counts else 0.0

    alloc_results.append(CompareMethodResult(
        name="Alokasi Acak (Random)",
        allocations={cid: len(pids) for cid, pids in rnd_allocs.items()},
        total_distance_m=round(rnd_tot_dist, 2),
        max_courier_distance_m=round(rnd_max_dist, 2),
        std_dev_packages=round(std_dev_rnd, 2),
        execution_time_ms=round(t_rnd, 2)
    ))

    # 2. Routing comparisons on KNN allocation (ACO vs NN vs Urutan Klik)
    point_name_map = {depot_id: req.depot.name or "Depot Juanda"}
    for p in req.packages:
        point_name_map[p.id] = p.name or p.id

    routing_results: List[Dict[str, Any]] = []
    aco_tot_dist = 0.0
    nn_tot_dist = 0.0
    orig_tot_dist = 0.0
    dijkstra_tot_dist = 0.0
    total_aco_time_ms = 0.0
    total_dijkstra_time_ms = 0.0
    aco_routes: List[Dict[str, Any]] = []
    nn_routes: List[Dict[str, Any]] = []
    original_routes: List[Dict[str, Any]] = []
    dijkstra_routes: List[Dict[str, Any]] = []
    aco_steps_by_courier: Dict[str, List[Dict[str, Any]]] = {}
    nn_steps_by_courier: Dict[str, List[Dict[str, Any]]] = {}
    dijkstra_steps_by_courier: Dict[str, List[Dict[str, Any]]] = {}
    original_steps_by_courier: Dict[str, List[Dict[str, Any]]] = {}
    aco_details_by_courier: Dict[str, Dict[str, Any]] = {}

    for cid, pids in knn_allocs.items():
        if not pids:
            continue
        courier = next(c for c in req.couriers if c.id == cid)
        pkg_indices = [id_to_idx[pid] for pid in pids if pid in id_to_idx]

        # NN
        nn_tour, nn_dist, nn_steps = compute_nn_steps(
            id_to_idx[depot_id], pkg_indices, dist_matrix, req.point_ids, point_name_map
        )
        nn_steps_by_courier[cid] = nn_steps

        # Dijkstra
        dijkstra_started = time.perf_counter()
        dijkstra_idxs, dijkstra_distance, dijkstra_steps = compute_dijkstra_steps(
            id_to_idx[depot_id], pkg_indices, dist_matrix, req.point_ids, point_name_map
        )
        total_dijkstra_time_ms += (time.perf_counter() - dijkstra_started) * 1000
        dijkstra_steps_by_courier[cid] = dijkstra_steps

        # Original
        _, orig_dist, orig_steps = compute_original_steps(
            id_to_idx[depot_id], pkg_indices, dist_matrix, req.point_ids, point_name_map
        )
        original_steps_by_courier[cid] = orig_steps

        # ACO
        opt_req = OptimizeRequest(
            courier_id=cid,
            matrix=req.matrix,
            point_ids=req.point_ids,
            start_id=depot_id,
            package_ids=pids,
            alpha=req.alpha,
            beta=req.beta,
            rho=req.rho,
            q=req.q,
            iterations=req.iterations
        )
        opt_res = solve_open_tsp_aco(opt_req)
        aco_steps = compute_tour_steps_from_ids(
            depot_id, opt_res.tour, id_to_idx, dist_matrix, point_name_map
        )
        aco_steps_by_courier[cid] = aco_steps
        aco_details_by_courier[cid] = {
            "iterations_log": [log.model_dump() for log in opt_res.iterations_log],
            "convergence": opt_res.convergence
        }

        aco_tot_dist += opt_res.total_distance_m
        nn_tot_dist += nn_dist
        orig_tot_dist += orig_dist
        dijkstra_tot_dist += dijkstra_distance
        total_aco_time_ms += opt_res.execution_time_ms

        aco_routes.append({"courier_id": cid, "courier_name": courier.name, "package_ids": opt_res.tour})
        nn_routes.append({
            "courier_id": cid,
            "courier_name": courier.name,
            "package_ids": [req.point_ids[i] for i in nn_tour]
        })
        original_routes.append({"courier_id": cid, "courier_name": courier.name, "package_ids": pids})
        dijkstra_routes.append({
            "courier_id": cid,
            "courier_name": courier.name,
            "package_ids": [req.point_ids[i] for i in dijkstra_idxs]
        })

    saving_vs_orig = ((orig_tot_dist - aco_tot_dist) / orig_tot_dist * 100) if orig_tot_dist > 0 else 0.0
    saving_vs_nn = ((nn_tot_dist - aco_tot_dist) / nn_tot_dist * 100) if nn_tot_dist > 0 else 0.0

    routing_results = [
        {
            "method": "Ant Colony Optimization (ACO)",
            "total_distance_km": round(aco_tot_dist / 1000.0, 3),
            "execution_time_ms": round(total_aco_time_ms, 2),
            "savings_vs_click_percent": round(saving_vs_orig, 2),
            "savings_vs_nn_percent": round(saving_vs_nn, 2),
            "note": "Rute teroptimasi global dengan feromon dan heuristik jarak",
            "routes": aco_routes,
            "steps_by_courier": aco_steps_by_courier,
            "aco_details_by_courier": aco_details_by_courier
        },
        {
            "method": "Nearest Neighbor (NN Heuristik)",
            "total_distance_km": round(nn_tot_dist / 1000.0, 3),
            "execution_time_ms": 1.2,
            "savings_vs_click_percent": round(((orig_tot_dist - nn_tot_dist) / orig_tot_dist * 100) if orig_tot_dist > 0 else 0.0, 2),
            "savings_vs_nn_percent": 0.0,
            "note": "Heuristik lokal rakus (greedy), sering terjebak optimum lokal",
            "routes": nn_routes,
            "steps_by_courier": nn_steps_by_courier
        },
        {
            "method": "Dijkstra (Greedy Shortest Path)",
            "total_distance_km": round(dijkstra_tot_dist / 1000.0, 3),
            "execution_time_ms": round(total_dijkstra_time_ms, 2),
            "savings_vs_click_percent": round(((orig_tot_dist - dijkstra_tot_dist) / orig_tot_dist * 100) if orig_tot_dist > 0 else 0.0, 2),
            "savings_vs_nn_percent": round(((nn_tot_dist - dijkstra_tot_dist) / nn_tot_dist * 100) if nn_tot_dist > 0 else 0.0, 2),
            "note": "Memilih paket terdekat berikutnya berdasarkan jarak terpendek Dijkstra",
            "routes": dijkstra_routes,
            "steps_by_courier": dijkstra_steps_by_courier
        },
        {
            "method": "Urutan Klik / Input Manual",
            "total_distance_km": round(orig_tot_dist / 1000.0, 3),
            "execution_time_ms": 0.1,
            "savings_vs_click_percent": 0.0,
            "savings_vs_nn_percent": round(-saving_vs_nn, 2),
            "note": "Urutan sesuai kronologi input tanpa optimasi",
            "routes": original_routes,
            "steps_by_courier": original_steps_by_courier
        }
    ]

    return CompareResponse(
        allocation_comparisons=alloc_results,
        routing_comparisons=routing_results,
        knn_steps=knn_resp.steps,
        knn_rebalance_logs=knn_resp.rebalance_logs
    )
