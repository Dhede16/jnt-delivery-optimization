import pytest
import numpy as np
from aco import solve_adaptive_tour, solve_open_tsp_aco
from schemas import OptimizeRequest


def test_adaptive_routing_direct_hop():
    matrix = [
        [0.0, 100.0],
        [100.0, 0.0]
    ]
    req = OptimizeRequest(
        courier_id="c1",
        matrix=matrix,
        point_ids=["depot", "pkg1"],
        start_id="depot",
        package_ids=["pkg1"],
        adaptive=True
    )
    res = solve_adaptive_tour(req)
    assert res.algorithm_used == "Direct Hop"
    assert res.tour == ["pkg1"]
    assert res.total_distance_m == 100.0


def test_adaptive_routing_exact_brute_force():
    # 4 packages -> Tier 2 (2 <= N <= 7)
    # depot at 0, packages at 1, 2, 3, 4 along a line: 0 -> 1 -> 2 -> 3 -> 4
    pts = ["depot", "p1", "p2", "p3", "p4"]
    coords = [0, 10, 20, 30, 40]
    n = len(coords)
    matrix = [[abs(coords[i] - coords[j]) * 100.0 for j in range(n)] for i in range(n)]

    req = OptimizeRequest(
        courier_id="c1",
        matrix=matrix,
        point_ids=pts,
        start_id="depot",
        package_ids=["p4", "p2", "p1", "p3"],
        adaptive=True
    )
    res = solve_open_tsp_aco(req)
    assert res.algorithm_used == "Exact Brute Force"
    assert "100% solusi optimal" in res.reasoning
    assert res.tour == ["p1", "p2", "p3", "p4"]
    assert res.total_distance_m == 4000.0


def test_adaptive_routing_nearest_neighbor():
    # 10 packages -> Tier 3 (8 <= N <= 14)
    pts = ["depot"] + [f"p{i}" for i in range(1, 11)]
    coords = list(range(len(pts)))
    n = len(coords)
    matrix = [[abs(coords[i] - coords[j]) * 50.0 for j in range(n)] for i in range(n)]

    req = OptimizeRequest(
        courier_id="c1",
        matrix=matrix,
        point_ids=pts,
        start_id="depot",
        package_ids=[f"p{i}" for i in range(1, 11)],
        adaptive=True
    )
    res = solve_open_tsp_aco(req)
    assert res.algorithm_used == "Nearest Neighbor"
    assert "8-14" in res.reasoning
    assert len(res.tour) == 10


def test_adaptive_routing_aco():
    # 16 packages -> Tier 4 (N >= 15)
    pts = ["depot"] + [f"p{i}" for i in range(1, 17)]
    coords = list(range(len(pts)))
    n = len(coords)
    matrix = [[abs(coords[i] - coords[j]) * 50.0 for j in range(n)] for i in range(n)]

    req = OptimizeRequest(
        courier_id="c1",
        matrix=matrix,
        point_ids=pts,
        start_id="depot",
        package_ids=[f"p{i}" for i in range(1, 17)],
        adaptive=True,
        iterations=10,
        n_ants=5
    )
    res = solve_open_tsp_aco(req)
    assert res.algorithm_used == "Ant Colony Optimization"
    assert ">=15" in res.reasoning
    assert len(res.tour) == 16
