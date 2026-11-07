import json
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from aco import solve_open_tsp_aco
from comparison import run_comparisons
from knn import run_knn_allocation
from osrm import (
    RoadDistanceError,
    get_distance_matrix,
    get_knn_road_distance_matrices,
    get_route_geometry,
)
from schemas import (
    AllocateRequest,
    AllocateResponse,
    CompareRequest,
    CompareResponse,
    GeometryRequest,
    GeometryResponse,
    MatrixRequest,
    MatrixResponse,
    OptimizeRequest,
    OptimizeResponse,
)

app = FastAPI(
    title="J&T Express Samarinda - KNN Multi-Courier & ACO Route Optimizer API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "scenarios.json"


@app.get("/api/config")
def get_config() -> Dict[str, Any]:
    """Returns default settings, depot coordinates, and limits."""
    return {
        "depot": {
            "id": "depot-jnt",
            "name": "J&T Express Drop Point Juanda Samarinda",
            "lat": -0.4897,
            "lng": 117.1352
        },
        "limits": {
            "max_couriers": 10,
            "max_packages": 50,
            "min_ref_points_per_courier": 1
        },
        "defaults": {
            "knn_k": 1,
            "balance_load": False,
            "aco_alpha": 1.0,
            "aco_beta": 3.0,
            "aco_rho": 0.5,
            "aco_q": 100.0,
            "aco_iterations": 100
        }
    }


@app.get("/api/scenarios")
def get_scenarios() -> Dict[str, Any]:
    """Loads pre-configured simulation scenarios for Samarinda."""
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Berkas skenario tidak ditemukan.")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/matrix", response_model=MatrixResponse)
async def post_matrix(req: MatrixRequest):
    """Calculates road distance matrix (or Haversine fallback) between depot and packages."""
    if len(req.packages) > 50:
        raise HTTPException(status_code=400, detail="Maksimal 50 paket diperbolehkan.")
    return await get_distance_matrix(req)


@app.post("/api/allocate", response_model=AllocateResponse)
async def post_allocate(req: AllocateRequest):
    """Allocates packages with scikit-learn KNN using OSRM road distances."""
    if len(req.couriers) == 0:
        raise HTTPException(status_code=400, detail="Minimal 1 kurir harus ditambahkan.")
    if len(req.couriers) > 10:
        raise HTTPException(status_code=400, detail="Maksimal 10 kurir diperbolehkan.")
    if len(req.packages) > 50:
        raise HTTPException(status_code=400, detail="Maksimal 50 paket diperbolehkan.")
    for c in req.couriers:
        if len(c.ref_points) < 1:
            raise HTTPException(status_code=400, detail=f"Kurir '{c.name}' belum memiliki titik acuan.")

    try:
        reference_distances, package_distances = await get_knn_road_distance_matrices(
            req.couriers, req.packages
        )
        return run_knn_allocation(req, reference_distances, package_distances)
    except RoadDistanceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/optimize", response_model=OptimizeResponse)
def post_optimize(req: OptimizeRequest):
    """Solves Open TSP using Ant Colony Optimization."""
    try:
        return solve_open_tsp_aco(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/geometry", response_model=GeometryResponse)
async def post_geometry(req: GeometryRequest):
    """Retrieves route GeoJSON geometry following real road networks."""
    geojson, dist_m, fallback = await get_route_geometry(req.coordinates)
    return GeometryResponse(
        geojson=geojson,
        total_distance_m=dist_m,
        is_haversine_fallback=fallback
    )


@app.post("/api/compare", response_model=CompareResponse)
async def post_compare(req: CompareRequest):
    """Compares allocation and routing methods using OSRM road distances for KNN."""
    try:
        reference_distances, package_distances = await get_knn_road_distance_matrices(
            req.couriers, req.packages
        )
        return run_comparisons(req, reference_distances, package_distances)
    except RoadDistanceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Serve Frontend Production Build if present
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
