import math
import pytest
from aco import brute_force_best_tour, nearest_neighbor_tour, solve_open_tsp_aco
from knn import haversine_km, run_knn_allocation
from schemas import (
    AllocateRequest,
    Courier,
    OptimizeRequest,
    Point,
)


def test_haversine():
    # Juanda to Pelabuhan Samarinda (~2.6 km)
    d = haversine_km(-0.4897, 117.1352, -0.5020, 117.1520)
    assert 2.0 < d < 3.5


def test_knn_allocation_basic():
    c1 = Courier(id="c1", name="Kurir 1", color="#3B82F6", ref_points=[
        Point(id="r1", name="R1", lat=-0.48, lng=117.13),
        Point(id="r2", name="R2", lat=-0.482, lng=117.131)
    ])
    c2 = Courier(id="c2", name="Kurir 2", color="#EF4444", ref_points=[
        Point(id="r3", name="R3", lat=-0.51, lng=117.15),
        Point(id="r4", name="R4", lat=-0.512, lng=117.151)
    ])

    p_near_c1 = Point(id="p1", name="P1", lat=-0.481, lng=117.1305)
    p_near_c2 = Point(id="p2", name="P2", lat=-0.511, lng=117.1505)

    req = AllocateRequest(
        couriers=[c1, c2],
        packages=[p_near_c1, p_near_c2],
        k=3,
        balance_load=False
    )
    res = run_knn_allocation(req)
    assert "p1" in res.allocations["c1"]
    assert "p2" in res.allocations["c2"]
    assert len(res.steps) == 2
    assert res.steps[0].winner_courier_id == "c1"


def test_knn_load_balancing():
    # 3 packages all physically closer to c1, but 2 couriers.
    # Max load per courier = ceil(3 / 2) = 2.
    # One package should be reallocated to c2.
    c1 = Courier(id="c1", name="Kurir 1", color="#3B82F6", ref_points=[
        Point(id="r1", name="R1", lat=-0.48, lng=117.13)
    ])
    c2 = Courier(id="c2", name="Kurir 2", color="#EF4444", ref_points=[
        Point(id="r2", name="R2", lat=-0.51, lng=117.15)
    ])
    pkgs = [
        Point(id="p1", name="P1", lat=-0.481, lng=117.130),
        Point(id="p2", name="P2", lat=-0.482, lng=117.131),
        Point(id="p3", name="P3", lat=-0.485, lng=117.132)  # furthest from c1
    ]
    req = AllocateRequest(couriers=[c1, c2], packages=pkgs, k=1, balance_load=True)
    res = run_knn_allocation(req)
    assert len(res.allocations["c1"]) == 2
    assert len(res.allocations["c2"]) == 1
    assert len(res.rebalance_logs) > 0


def test_aco_open_tsp_vs_brute_force():
    # Small instance: 4 packages, depot at index 0
    # Symmetric 5x5 matrix
    coords = [
        (0.0, 0.0),  # depot
        (1.0, 0.0),  # p1
        (2.0, 0.0),  # p2
        (3.0, 0.0),  # p3
        (4.0, 0.0),  # p4
    ]
    n = len(coords)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            matrix[i][j] = abs(coords[i][0] - coords[j][0]) * 1000.0

    point_ids = ["depot", "p1", "p2", "p3", "p4"]
    pkg_ids = ["p1", "p2", "p3", "p4"]

    # True optimal open TSP from depot (0,0) visiting (1,0),(2,0),(3,0),(4,0) in line has distance = 4000.0
    req = OptimizeRequest(
        matrix=matrix,
        point_ids=point_ids,
        start_id="depot",
        package_ids=pkg_ids,
        alpha=1.0,
        beta=3.0,
        rho=0.5,
        q=100.0,
        iterations=50
    )
    res = solve_open_tsp_aco(req)
    assert len(res.tour) == 4
    assert res.total_distance_m == 4000.0


def test_aco_single_package():
    matrix = [[0.0, 1500.0], [1500.0, 0.0]]
    req = OptimizeRequest(
        matrix=matrix,
        point_ids=["depot", "p1"],
        start_id="depot",
        package_ids=["p1"]
    )
    res = solve_open_tsp_aco(req)
    assert res.tour == ["p1"]
    assert res.total_distance_m == 1500.0

