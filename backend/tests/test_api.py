from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


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


def test_allocate_and_optimize_endpoints():
    scenario_res = client.get("/api/scenarios")
    s10 = scenario_res.json()["scenarios"][0]

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

