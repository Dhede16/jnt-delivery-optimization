from fastapi.testclient import TestClient
import main
from osrm import RoadDistanceError

client = TestClient(main.app)


def test_get_config():
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert data["depot"]["id"] == "depot-jnt"
    assert data["limits"]["max_packages"] == 50


def test_get_scenarios():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 4


def test_allocate_and_optimize_endpoints(monkeypatch):
    scenario_res = client.get("/api/scenarios")
    s10 = scenario_res.json()["scenarios"][0]

    async def road_distances(couriers, packages):
        reference_count = sum(len(c.ref_points) for c in couriers)
        reference_matrix = [
            [0.0 if i == j else 1000.0 for j in range(reference_count)]
            for i in range(reference_count)
        ]
        package_matrix = [[500.0] * reference_count for _ in packages]
        return reference_matrix, package_matrix

    monkeypatch.setattr(main, "get_knn_road_distance_matrices", road_distances)

    # Test allocate
    alloc_req = {
        "couriers": s10["couriers"],
        "packages": s10["packages"],
        "k": 3,
        "balance_load": False
    }
    alloc_res = client.post("/api/allocate", json=alloc_req)
    assert alloc_res.status_code == 200
    alloc_data = alloc_res.json()
    assert len(alloc_data["steps"]) == 10

    # Build dummy matrix for 10 packages + depot
    n = 11
    matrix = [[1000.0 if i != j else 0.0 for j in range(n)] for i in range(n)]
    point_ids = ["depot-jnt"] + [p["id"] for p in s10["packages"]]

    c1_pkgs = alloc_data["allocations"]["c1"]
    opt_req = {
        "courier_id": "c1",
        "matrix": matrix,
        "point_ids": point_ids,
        "start_id": "depot-jnt",
        "package_ids": c1_pkgs,
        "alpha": 1.0,
        "beta": 3.0,
        "rho": 0.5,
        "q": 100.0,
        "iterations": 20
    }
    opt_res = client.post("/api/optimize", json=opt_req)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert len(opt_data["tour"]) == len(c1_pkgs)
    assert opt_data["total_distance_m"] > 0


def test_allocate_returns_service_unavailable_when_osrm_fails(monkeypatch):
    async def unavailable(couriers, packages):
        raise RoadDistanceError("OSRM tidak tersedia.")

    monkeypatch.setattr(main, "get_knn_road_distance_matrices", unavailable)
    response = client.post("/api/allocate", json={
        "couriers": [{
            "id": "c1",
            "name": "Kurir 1",
            "color": "#3B82F6",
            "ref_points": [{"id": "r1", "lat": 0.0, "lng": 0.0}]
        }],
        "packages": [{"id": "p1", "lat": 0.1, "lng": 0.1}]
    })

    assert response.status_code == 503
    assert response.json()["detail"] == "OSRM tidak tersedia."
