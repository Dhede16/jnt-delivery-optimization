from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LatLng(BaseModel):
    lat: float
    lng: float


class Point(BaseModel):
    id: str
    name: str = ""
    lat: float
    lng: float
    courier_id: Optional[str] = None
    order: Optional[int] = None


class Courier(BaseModel):
    id: str
    name: str
    color: str
    ref_points: List[Point] = Field(default_factory=list)


class MatrixRequest(BaseModel):
    depot: Point
    packages: List[Point]


class MatrixResponse(BaseModel):
    matrix: List[List[float]]
    point_ids: List[str]
    is_haversine_fallback: bool
    source_message: str = ""


class NeighborVote(BaseModel):
    ref_point_id: str
    courier_id: str
    distance_km: float
    weight: float


class KNNStepDetail(BaseModel):
    package_id: str
    package_name: str
    package_lat: float
    package_lng: float
    all_distances: List[Dict[str, Any]]
    top_k: List[NeighborVote]
    vote_counts: Dict[str, int]
    vote_weights: Dict[str, float]
    winner_courier_id: str
    tie_broken: bool = False
    rebalanced: bool = False
    rebalanced_reason: str = ""


class AllocateRequest(BaseModel):
    couriers: List[Courier]
    packages: List[Point]
    k: int = 3
    balance_load: bool = False


class AllocateResponse(BaseModel):
    allocations: Dict[str, List[str]]
    steps: List[KNNStepDetail]
    rebalance_logs: List[str]
    effective_k: int
    warning: Optional[str] = None


class ACOIterationLog(BaseModel):
    iteration: int
    best_tour: List[str]
    best_distance_m: float
    avg_distance_m: float


class OptimizeRequest(BaseModel):
    courier_id: Optional[str] = None
    matrix: List[List[float]]
    point_ids: List[str]
    start_id: str
    package_ids: List[str]
    alpha: float = 1.0
    beta: float = 3.0
    rho: float = 0.5
    q: float = 100.0
    n_ants: Optional[int] = None
    iterations: int = 100


class OptimizeResponse(BaseModel):
    courier_id: Optional[str] = None
    tour: List[str]
    total_distance_m: float
    iterations_log: List[ACOIterationLog]
    convergence: List[float]
    execution_time_ms: float
    nn_distance_m: float
    original_order_distance_m: float


class GeometryRequest(BaseModel):
    coordinates: List[List[float]]


class GeometryResponse(BaseModel):
    geojson: Dict[str, Any]
    total_distance_m: float
    is_haversine_fallback: bool


class CompareRequest(BaseModel):
    couriers: List[Courier]
    packages: List[Point]
    depot: Point
    matrix: List[List[float]]
    point_ids: List[str]
    k: int = 3
    balance_load: bool = False
    alpha: float = 1.0
    beta: float = 3.0
    rho: float = 0.5
    q: float = 100.0
    iterations: int = 100


class CompareMethodResult(BaseModel):
    name: str
    allocations: Dict[str, int]
    total_distance_m: float
    max_courier_distance_m: float
    std_dev_packages: float
    execution_time_ms: float


class CompareResponse(BaseModel):
    allocation_comparisons: List[CompareMethodResult]
    routing_comparisons: List[Dict[str, Any]]

