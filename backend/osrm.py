import logging
import math
from typing import Any, Dict, List, Tuple
import httpx
from knn import haversine_km
from schemas import Courier, MatrixRequest, MatrixResponse, Point

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "https://router.project-osrm.org"
OSRM_TABLE_BATCH_SIZE = 50


class RoadDistanceError(RuntimeError):
    pass


async def get_knn_road_distance_matrices(
    couriers: List[Courier],
    packages: List[Point]
) -> Tuple[List[List[float]], List[List[float]]]:
    reference_points = [point for courier in couriers for point in courier.ref_points]
    if not reference_points:
        raise RoadDistanceError("Tidak ada titik acuan untuk menghitung jarak jalan.")

    sources = [(point, "reference", i) for i, point in enumerate(reference_points)]
    sources.extend((point, "package", i) for i, point in enumerate(packages))
    reference_distances = [[0.0] * len(reference_points) for _ in reference_points]
    package_distances = [[0.0] * len(reference_points) for _ in packages]

    async with httpx.AsyncClient(timeout=8.0) as client:
        for source_start in range(0, len(sources), OSRM_TABLE_BATCH_SIZE):
            source_batch = sources[source_start:source_start + OSRM_TABLE_BATCH_SIZE]
            for destination_start in range(0, len(reference_points), OSRM_TABLE_BATCH_SIZE):
                destination_batch = reference_points[
                    destination_start:destination_start + OSRM_TABLE_BATCH_SIZE
                ]
                coordinates = [point for point, _, _ in source_batch] + destination_batch
                coords_str = ";".join(
                    f"{point.lng:.6f},{point.lat:.6f}" for point in coordinates
                )
                source_indices = ";".join(str(i) for i in range(len(source_batch)))
                destination_indices = ";".join(
                    str(len(source_batch) + i) for i in range(len(destination_batch))
                )
                url = (
                    f"{OSRM_BASE_URL}/table/v1/driving/{coords_str}"
                    f"?annotations=distance&sources={source_indices}"
                    f"&destinations={destination_indices}"
                )

                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                except (httpx.HTTPError, ValueError) as exc:
                    raise RoadDistanceError(
                        "Gagal memperoleh jarak jalan dari OSRM. Coba lagi saat layanan tersedia."
                    ) from exc

                if not isinstance(data, dict):
                    raise RoadDistanceError("OSRM mengembalikan respons yang tidak valid.")
                values = data.get("distances")
                if data.get("code") != "Ok" or not isinstance(values, list):
                    raise RoadDistanceError(
                        f"OSRM gagal menghitung jarak jalan: {data.get('message', data.get('code', 'respons tidak valid'))}."
                    )
                if len(values) != len(source_batch):
                    raise RoadDistanceError("OSRM mengembalikan matriks jarak yang tidak lengkap.")

                for source_index, row in enumerate(values):
                    if not isinstance(row, list) or len(row) != len(destination_batch):
                        raise RoadDistanceError("OSRM mengembalikan matriks jarak yang tidak valid.")
                    point, source_type, result_index = source_batch[source_index]
                    for destination_index, distance_m in enumerate(row):
                        destination = destination_batch[destination_index]
                        if distance_m is None:
                            raise RoadDistanceError(
                                f"Tidak ada rute jalan OSRM antara '{point.id}' dan '{destination.id}'."
                            )
                        try:
                            distance_m = float(distance_m)
                        except (TypeError, ValueError) as exc:
                            raise RoadDistanceError(
                                "OSRM mengembalikan nilai jarak yang tidak valid."
                            ) from exc
                        if not math.isfinite(distance_m) or distance_m < 0:
                            raise RoadDistanceError("OSRM mengembalikan nilai jarak yang tidak valid.")
                        if source_type == "reference":
                            reference_distances[result_index][destination_start + destination_index] = distance_m
                        else:
                            package_distances[result_index][destination_start + destination_index] = distance_m

    return reference_distances, package_distances


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
