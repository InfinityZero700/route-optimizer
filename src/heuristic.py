"""Geographic great-circle heuristic (meters) for unprojected OSMnx graphs."""
import math

EARTH_RADIUS_METERS = 6_371_000.0


def haversine_coords(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return approximate great-circle distance in meters."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))


def haversine_distance(graph, node, goal) -> float:
    """Estimate node-to-goal distance; requires latitude y and longitude x."""
    u, v = graph.nodes[node], graph.nodes[goal]
    return haversine_coords(u['y'], u['x'], v['y'], v['x'])
