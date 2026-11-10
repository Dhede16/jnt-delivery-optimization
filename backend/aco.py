import heapq
import itertools
import math
import time
from typing import Dict, List, Tuple
import numpy as np
from schemas import ACOIterationLog, OptimizeRequest, OptimizeResponse


def nearest_neighbor_tour(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray
) -> Tuple[List[int], float]:
    """Computes a greedy Nearest Neighbor open TSP tour."""
    unvisited = set(pkg_indices)
    curr = start_idx
    tour = []
    total_dist = 0.0

    while unvisited:
        next_idx = min(unvisited, key=lambda u: dist_matrix[curr, u])
        total_dist += dist_matrix[curr, next_idx]
        tour.append(next_idx)
        unvisited.remove(next_idx)
        curr = next_idx

    return tour, total_dist


def dijkstra_tour(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray
) -> Tuple[List[int], float]:
    """Greedily visits the nearest remaining package using Dijkstra distances."""
    unvisited = set(pkg_indices)
    current = start_idx
    tour = []
    total_dist = 0.0
    n_points = dist_matrix.shape[0]

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

        next_idx = min(unvisited, key=lambda idx: distances[idx])
        total_dist += distances[next_idx]
        tour.append(next_idx)
        unvisited.remove(next_idx)
        current = next_idx

    return tour, total_dist


def original_order_tour(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray
) -> Tuple[List[int], float]:
    """Computes tour following the original given order."""
    if not pkg_indices:
        return [], 0.0
    total_dist = dist_matrix[start_idx, pkg_indices[0]]
    for i in range(len(pkg_indices) - 1):
        total_dist += dist_matrix[pkg_indices[i], pkg_indices[i + 1]]
    return list(pkg_indices), total_dist


def brute_force_best_tour(
    start_idx: int,
    pkg_indices: List[int],
    dist_matrix: np.ndarray
) -> Tuple[List[int], float]:
    """Brute force optimal search (only for small size <= 8)."""
    if len(pkg_indices) > 8:
        raise ValueError("Brute force hanya didukung untuk maksimal 8 paket.")
    if not pkg_indices:
        return [], 0.0

    best_dist = float("inf")
    best_perm: List[int] = []

    for perm in itertools.permutations(pkg_indices):
        d = dist_matrix[start_idx, perm[0]]
        for i in range(len(perm) - 1):
            d += dist_matrix[perm[i], perm[i + 1]]
        if d < best_dist:
            best_dist = d
            best_perm = list(perm)

    return best_perm, best_dist


def solve_open_tsp_aco(req: OptimizeRequest) -> OptimizeResponse:
    start_time = time.perf_counter()

    # Index mapping
    id_to_idx = {pid: i for i, pid in enumerate(req.point_ids)}
    if req.start_id not in id_to_idx:
        raise ValueError(f"Titik awal '{req.start_id}' tidak ditemukan di matriks.")

    start_idx = id_to_idx[req.start_id]
    pkg_indices = [id_to_idx[pid] for pid in req.package_ids if pid in id_to_idx]

    dist_matrix = np.array(req.matrix, dtype=np.float64)
    n_points = dist_matrix.shape[0]

    # Edge cases
    if len(pkg_indices) == 0:
        return OptimizeResponse(
            courier_id=req.courier_id,
            tour=[],
            total_distance_m=0.0,
            iterations_log=[],
            convergence=[],
            execution_time_ms=0.0,
            nn_distance_m=0.0,
            original_order_distance_m=0.0
        )

    if len(pkg_indices) == 1:
        d = float(dist_matrix[start_idx, pkg_indices[0]])
        return OptimizeResponse(
            courier_id=req.courier_id,
            tour=[req.point_ids[pkg_indices[0]]],
            total_distance_m=round(d, 2),
            iterations_log=[
                ACOIterationLog(
                    iteration=1,
                    best_tour=[req.point_ids[pkg_indices[0]]],
                    best_distance_m=round(d, 2),
                    avg_distance_m=round(d, 2)
                )
            ],
            convergence=[round(d, 2)],
            execution_time_ms=round((time.perf_counter() - start_time) * 1000, 2),
            nn_distance_m=round(d, 2),
            original_order_distance_m=round(d, 2)
        )

    # Baselines
    nn_tour, nn_dist = nearest_neighbor_tour(start_idx, pkg_indices, dist_matrix)
    orig_tour, orig_dist = original_order_tour(start_idx, pkg_indices, dist_matrix)

    # ACO Setup
    n_pkgs = len(pkg_indices)
    n_ants = req.n_ants if (req.n_ants and req.n_ants > 0) else max(n_pkgs, 5)
    iterations = max(req.iterations, 1)
    alpha = float(req.alpha)
    beta = float(req.beta)
    rho = float(req.rho)
    q_val = float(req.q)

    # Initial pheromone tau0 = 1 / (n * L_nn) or 1.0
    tau0 = 1.0 / (n_pkgs * max(nn_dist, 1.0)) if nn_dist > 0 else 1.0
    pheromone = np.full((n_points, n_points), tau0, dtype=np.float64)

    # Visibility eta = 1 / distance
    eps = 1e-4
    visibility = 1.0 / (dist_matrix + eps)
    np.fill_diagonal(visibility, 0.0)

    best_tour_overall: List[int] = list(nn_tour)
    best_dist_overall: float = float(nn_dist)

    convergence: List[float] = []
    iterations_log: List[ACOIterationLog] = []

    # Pre-calculated cache
    eta_beta = visibility ** beta

    # ACO Loop
    for it in range(iterations):
        tau_alpha = pheromone ** alpha
        all_ant_tours: List[List[int]] = []
        all_ant_lengths: List[float] = []

        for _ in range(n_ants):
            current = start_idx
            unvisited = list(pkg_indices)
            ant_tour: List[int] = []
            tour_len = 0.0

            while unvisited:
                # Transition probabilities
                p_values = tau_alpha[current, unvisited] * eta_beta[current, unvisited]
                p_sum = np.sum(p_values)

                if p_sum <= 0 or np.isnan(p_sum):
                    # Fallback to uniform random
                    probs = np.ones(len(unvisited)) / len(unvisited)
                else:
                    probs = p_values / p_sum

                next_city = np.random.choice(unvisited, p=probs)
                tour_len += dist_matrix[current, next_city]
                ant_tour.append(next_city)
                unvisited.remove(next_city)
                current = next_city

            all_ant_tours.append(ant_tour)
            all_ant_lengths.append(tour_len)

            if tour_len < best_dist_overall:
                best_dist_overall = tour_len
                best_tour_overall = list(ant_tour)

        # Evaporation
        pheromone *= (1.0 - rho)

        # Deposit pheromone from all ants
        for tour, length in zip(all_ant_tours, all_ant_lengths):
            if length > 0:
                deposit = q_val / length
                # Edge from start to first package
                c_prev = start_idx
                for c_curr in tour:
                    pheromone[c_prev, c_curr] += deposit
                    c_prev = c_curr

        # Elite pheromone reinforcement for the best overall
        if best_dist_overall > 0:
            elite_deposit = (q_val / best_dist_overall) * 2.0
            c_prev = start_idx
            for c_curr in best_tour_overall:
                pheromone[c_prev, c_curr] += elite_deposit
                c_prev = c_curr

        # Keep tau within reasonable bounds to prevent numerical under/overflow
        pheromone = np.clip(pheromone, 1e-10, 1e5)

        avg_dist = float(np.mean(all_ant_lengths))
        convergence.append(round(best_dist_overall, 2))

        # Log iteration milestone (every 10 or first 5 and last)
        if it < 5 or (it + 1) % 10 == 0 or it == iterations - 1:
            iterations_log.append(ACOIterationLog(
                iteration=it + 1,
                best_tour=[req.point_ids[idx] for idx in best_tour_overall],
                best_distance_m=round(best_dist_overall, 2),
                avg_distance_m=round(avg_dist, 2)
            ))

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return OptimizeResponse(
        courier_id=req.courier_id,
        tour=[req.point_ids[idx] for idx in best_tour_overall],
        total_distance_m=round(best_dist_overall, 2),
        iterations_log=iterations_log,
        convergence=convergence,
        execution_time_ms=round(elapsed_ms, 2),
        nn_distance_m=round(nn_dist, 2),
        original_order_distance_m=round(orig_dist, 2)
    )
