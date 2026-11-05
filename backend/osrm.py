import logging
from typing import Any, Dict, List, Tuple
import httpx
from knn import haversine_km
from schemas import MatrixRequest, MatrixResponse, Point

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "https://router.project-osrm.org"


def compute_haversine_matrix(points: List[Point]) -> Tuple[List[List[float]], List[str]]:
    n = len(points)
    matrix = [[0.0] * n for _ in range(n)]
    point_ids = [p.id for p in points]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0.0
            else:
                dist_km = haversine_km(points[i].lat, points[i].lng, points[j].lat, points[j].lng)
                matrix[i][j] = round(dist_km * 1000.0, 2)  # In meters
    return matrix, point_ids


async def get_distance_matrix(req: MatrixRequest) -> MatrixResponse:
    all_points = [req.depot] + req.packages
    point_ids = [p.id for p in all_points]
    n = len(all_points)

    if n <= 1:
        return MatrixResponse(
            matrix=[[0.0]],
            point_ids=point_ids,
            is_haversine_fallback=False,
            source_message="Hanya ada 1 titik (depot)."
        )

    # Format OSRM coordinate list: lon,lat;lon,lat;...
    coords_str = ";".join([f"{p.lng:.6f},{p.lat:.6f}" for p in all_points])
    url = f"{OSRM_BASE_URL}/table/v1/driving/{coords_str}?annotations=distance"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and "distances" in data:
                    raw_matrix = data["distances"]
                    # Check for any None values in table
                    matrix = []
                    has_none = False
                    for i in range(n):
                        row = []
                        for j in range(n):
                            val = raw_matrix[i][j]
                            if val is None:
                                has_none = True
                                # Haversine fallback for this cell
                                fallback_d = haversine_km(all_points[i].lat, all_points[i].lng, all_points[j].lat, all_points[j].lng) * 1000.0
                                row.append(round(fallback_d, 2))
                            else:
                                row.append(round(float(val), 2))
                        matrix.append(row)

                    if not has_none:
                        return MatrixResponse(
                            matrix=matrix,
                            point_ids=point_ids,
                            is_haversine_fallback=False,
                            source_message="Matriks jarak jalan berhasil diperoleh dari OSRM."
                        )
                    else:
                        return MatrixResponse(
                            matrix=matrix,
                            point_ids=point_ids,
                            is_haversine_fallback=True,
                            source_message="Sebagian rute tidak terhubung OSRM; sel yang kosong dihitung dengan Haversine."
                        )
    except Exception as e:
        logger.warning(f"OSRM table call failed ({e}). Menggunakan fallback Haversine.")

    # Fallback entirely to Haversine
    matrix, _ = compute_haversine_matrix(all_points)
    return MatrixResponse(
        matrix=matrix,
        point_ids=point_ids,
        is_haversine_fallback=True,
        source_message="OSRM tidak merespon/terbatas. Matriks jarak menggunakan rumus Haversine (garis lurus)."
    )


async def get_route_geometry(coordinates: List[List[float]]) -> Tuple[Dict[str, Any], float, bool]:
    """
    coordinates: List of [lat, lng].
    Returns (geojson_dict, total_distance_m, is_haversine_fallback).
    """
    if len(coordinates) < 2:
        return {
            "type": "LineString",
            "coordinates": [[coord[1], coord[0]] for coord in coordinates]
        }, 0.0, False

    # OSRM expects lon,lat
    coords_str = ";".join([f"{coord[1]:.6f},{coord[0]:.6f}" for coord in coordinates])
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}?overview=full&geometries=geojson"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    primary_route = data["routes"][0]
                    distance_m = float(primary_route.get("distance", 0.0))
                    geometry = primary_route.get("geometry", {})
                    return geometry, round(distance_m, 2), False
    except Exception as e:
        logger.warning(f"OSRM route geometry failed ({e}). Menggunakan garis lurus.")

    # Fallback: straight lines between points
    straight_line_coords = [[coord[1], coord[0]] for coord in coordinates]
    total_m = 0.0
    for i in range(len(coordinates) - 1):
        total_m += haversine_km(
            coordinates[i][0], coordinates[i][1],
            coordinates[i + 1][0], coordinates[i + 1][1]
        ) * 1000.0

    return {
        "type": "LineString",
        "coordinates": straight_line_coords
    }, round(total_m, 2), True

