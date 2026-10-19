"""From-scratch shortest path solvers for directed graphs and multigraphs."""
from dataclasses import dataclass
import heapq
import itertools
import math
from .heuristic import haversine_distance


@dataclass
class RouteResult:
    path: list
    distance_m: float
    nodes_explored: int


def _edge_weight(graph, u, v):
    data = graph.get_edge_data(u, v)
    if graph.is_multigraph():
        return min(float(edge['length']) for edge in data.values())
    return float(data['length'])


def compute_route(graph, source, target, algorithm='dijkstra') -> RouteResult:
    """Find a minimum-length route with Dijkstra or A*.

    Edge 'length' values must be finite, nonnegative meters. For A*, node
    coordinates must be unprojected latitude/longitude with 'y'/'x' keys;
    edge lengths must be >= the great-circle separation of edge endpoints.
    """
    if algorithm not in ('dijkstra', 'astar'):
        raise ValueError("algorithm must be 'dijkstra' or 'astar'")
    if source not in graph or target not in graph:
        raise ValueError('source and target must be graph nodes')
    if source == target:
        return RouteResult([source], 0.0, 1)

    def h(node):
        return haversine_distance(graph, node, target) if algorithm == 'astar' else 0.0

    counter = itertools.count()
    frontier = [(h(source), 0.0, next(counter), source)]
    best = {source: 0.0}
    parent = {}
    explored = 0
    while frontier:
        _, g, _, u = heapq.heappop(frontier)
        if g > best[u] + 1e-9:
            continue
        explored += 1
        if u == target:
            path = [target]
            while path[-1] != source:
                path.append(parent[path[-1]])
            path.reverse()
            return RouteResult(path, g, explored)
        for v in graph.successors(u) if graph.is_directed() else graph.neighbors(u):
            w = _edge_weight(graph, u, v)
            if not math.isfinite(w) or w < 0:
                raise ValueError('edge lengths must be finite and nonnegative')
            new_g = g + w
            if new_g < best.get(v, math.inf) - 1e-9:
                best[v], parent[v] = new_g, u
                heapq.heappush(frontier, (new_g + h(v), new_g, next(counter), v))
    return RouteResult([], math.inf, explored)
