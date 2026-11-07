import math
from typing import Dict, List, Tuple
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from schemas import AllocateRequest, AllocateResponse, KNNStepDetail, NeighborVote


def real_distance_knn(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def run_knn_allocation(
    req: AllocateRequest,
    reference_distances_m: List[List[float]],
    package_distances_m: List[List[float]]
) -> AllocateResponse:
    # 1. Gather all training reference points
    training_points: List[Tuple[str, str, float, float]] = []  # (ref_id, courier_id, lat, lng)
    for courier in req.couriers:
        for rp in courier.ref_points:
            training_points.append((rp.id, courier.id, rp.lat, rp.lng))

    if not training_points:
        raise ValueError("Setiap kurir harus memiliki minimal 1 titik acuan.")

    total_ref_points = len(training_points)
    effective_k = req.k
    warning_msg = None
    if effective_k > total_ref_points:
        effective_k = total_ref_points
        warning_msg = f"Nilai k ({req.k}) melebihi total titik acuan ({total_ref_points}). k disesuaikan menjadi {effective_k}."
    if effective_k < 1:
        effective_k = 1

    if len(reference_distances_m) != total_ref_points or any(
        len(row) != total_ref_points for row in reference_distances_m
    ):
        raise ValueError("Matriks jarak antar titik acuan tidak valid.")
    if len(package_distances_m) != len(req.packages) or any(
        len(row) != total_ref_points for row in package_distances_m
    ):
        raise ValueError("Matriks jarak paket ke titik acuan tidak valid.")

    classifier = KNeighborsClassifier(
        n_neighbors=effective_k,
        metric="precomputed"
    ).fit(np.asarray(reference_distances_m), [p[1] for p in training_points])
    package_distances = np.asarray(package_distances_m)
    if req.packages:
        predicted_couriers = classifier.predict(package_distances)
        neighbor_distances, neighbor_indices = classifier.kneighbors(
            package_distances,
            n_neighbors=total_ref_points
        )
    else:
        predicted_couriers = []
        neighbor_distances = np.empty((0, total_ref_points))
        neighbor_indices = np.empty((0, total_ref_points), dtype=int)

    steps: List[KNNStepDetail] = []
    initial_allocations: Dict[str, List[str]] = {c.id: [] for c in req.couriers}
    package_courier_rankings: Dict[str, List[str]] = {}
    package_dist_to_winner_rp: Dict[str, float] = {}

    eps = 1e-7

    # 2. Allocate each package with KNN
    for package_index, pkg in enumerate(req.packages):
        distances = []
        for distance_m, reference_index in zip(
            neighbor_distances[package_index],
            neighbor_indices[package_index]
        ):
            ref_id, courier_id, _, _ = training_points[reference_index]
            dist_km = distance_m / 1000.0
            distances.append({
                "ref_point_id": ref_id,
                "courier_id": courier_id,
                "distance_km": round(dist_km, 4),
                "weight": round(1.0 / (dist_km + eps), 4)
            })
        top_k_items = distances[:effective_k]

        vote_counts: Dict[str, int] = {}
        vote_weights: Dict[str, float] = {}
        for item in top_k_items:
            cid = item["courier_id"]
            vote_counts[cid] = vote_counts.get(cid, 0) + 1
            vote_weights[cid] = vote_weights.get(cid, 0.0) + item["weight"]

        # Determine winner by majority vote
        max_votes = max(vote_counts.values())
        candidate_winners = [cid for cid, v in vote_counts.items() if v == max_votes]

        tie_broken = False
        if len(candidate_winners) == 1:
            winner = predicted_couriers[package_index]
        else:
            # Tie breaking by highest inverse-distance weight
            tie_broken = True
            candidate_winners.sort(key=lambda cid: vote_weights.get(cid, 0.0), reverse=True)
            winner = candidate_winners[0]

        # Rank all couriers by proximity to this package for potential rebalancing
        courier_best_dist: Dict[str, float] = {}
        for item in distances:
            cid = item["courier_id"]
            if cid not in courier_best_dist:
                courier_best_dist[cid] = item["distance_km"]
        # Ordered couriers by distance
        ranked_couriers = sorted(courier_best_dist.keys(), key=lambda c: courier_best_dist[c])
        package_courier_rankings[pkg.id] = ranked_couriers

        # Distance to winner's closest reference point
        winner_min_dist = courier_best_dist.get(winner, 0.0)
        package_dist_to_winner_rp[pkg.id] = winner_min_dist

        top_k_votes = [
            NeighborVote(
                ref_point_id=it["ref_point_id"],
                courier_id=it["courier_id"],
                distance_km=it["distance_km"],
                weight=it["weight"]
            )
            for it in top_k_items
        ]

        step = KNNStepDetail(
            package_id=pkg.id,
            package_name=pkg.name or pkg.id,
            package_lat=pkg.lat,
            package_lng=pkg.lng,
            all_distances=distances,
            top_k=top_k_votes,
            vote_counts=vote_counts,
            vote_weights={k: round(v, 4) for k, v in vote_weights.items()},
            winner_courier_id=winner,
            tie_broken=tie_broken,
            rebalanced=False,
            rebalanced_reason=""
        )
        steps.append(step)
        initial_allocations[winner].append(pkg.id)

    # 3. Optional Load Balancing
    rebalance_logs: List[str] = []
    final_allocations = {c.id: list(initial_allocations[c.id]) for c in req.couriers}

    if req.balance_load and len(req.packages) > 0 and len(req.couriers) > 0:
        max_load = math.ceil(len(req.packages) / len(req.couriers))
        rebalance_logs.append(f"Maksimal beban target per kurir: ceil({len(req.packages)}/{len(req.couriers)}) = {max_load} paket.")

        # Rebalancing loop
        iteration = 0
        step_dict = {s.package_id: s for s in steps}

        while any(len(final_allocations[c.id]) > max_load for c in req.couriers) and iteration < 100:
            iteration += 1
            overloaded_couriers = [c.id for c in req.couriers if len(final_allocations[c.id]) > max_load]
            if not overloaded_couriers:
                break

            # Pick the most overloaded courier
            overloaded_cid = max(overloaded_couriers, key=lambda cid: len(final_allocations[cid]))
            current_pkgs = final_allocations[overloaded_cid]

            # Find package furthest from this courier's reference points
            pkg_to_move = max(current_pkgs, key=lambda pid: package_dist_to_winner_rp.get(pid, 0.0))

            # Candidate underloaded couriers
            rankings = package_courier_rankings.get(pkg_to_move, [])
            target_cid = None
            for cid in rankings:
                if cid != overloaded_cid and len(final_allocations[cid]) < max_load:
                    target_cid = cid
                    break

            if not target_cid:
                # Any courier with strictly fewer packages
                candidates = [c.id for c in req.couriers if len(final_allocations[c.id]) < len(final_allocations[overloaded_cid]) - 1]
                if candidates:
                    target_cid = min(candidates, key=lambda cid: len(final_allocations[cid]))

            if target_cid:
                final_allocations[overloaded_cid].remove(pkg_to_move)
                final_allocations[target_cid].append(pkg_to_move)

                log_entry = (f"Paket {pkg_to_move} dipindah dari kurir '{overloaded_cid}' "
                             f"ke kurir '{target_cid}' (Beban sekarang: {len(final_allocations[overloaded_cid])} & {len(final_allocations[target_cid])})")
                rebalance_logs.append(log_entry)

                if pkg_to_move in step_dict:
                    step_dict[pkg_to_move].rebalanced = True
                    step_dict[pkg_to_move].winner_courier_id = target_cid
                    step_dict[pkg_to_move].rebalanced_reason = (
                        f"Dipindah dari {overloaded_cid} ke {target_cid} untuk meratakan beban (batas {max_load})."
                    )
            else:
                break

    return AllocateResponse(
        allocations=final_allocations,
        steps=steps,
        rebalance_logs=rebalance_logs,
        effective_k=effective_k,
        warning=warning_msg
    )
