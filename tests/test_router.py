"""Offline tests with tiny known graphs; no OSM API required."""
import math
import networkx as nx
import pytest
from src.heuristic import haversine_coords
from src.router import compute_route


def tiny_graph():
    g = nx.MultiDiGraph()
    # At the equator, 0.001 longitude degrees is approximately 111.2 m.
    g.add_node('S', y=0, x=0)
    g.add_node('A', y=0, x=0.001)
    g.add_node('T', y=0, x=0.002)
    g.add_edge('S', 'A', length=120)
    g.add_edge('A', 'T', length=120)
    g.add_edge('S', 'T', length=500)
    return g


@pytest.mark.parametrize('algorithm', ['dijkstra', 'astar'])
def test_shortest_route(algorithm):
    result = compute_route(tiny_graph(), 'S', 'T', algorithm)
    assert result.path == ['S', 'A', 'T']
    assert result.distance_m == 240


def test_matches_networkx_dijkstra():
    g = tiny_graph()
    expected = nx.shortest_path_length(g, 'S', 'T', weight='length')
    for alg in ('dijkstra', 'astar'):
        assert math.isclose(compute_route(g, 'S', 'T', alg).distance_m, expected)


def test_trivial_and_unreachable():
    g = tiny_graph()
    assert compute_route(g, 'S', 'S').distance_m == 0
    assert compute_route(g, 'T', 'S').path == []


def test_haversine_basics():
    assert haversine_coords(0, 0, 0, 0) == 0
    assert 110_000 < haversine_coords(0, 0, 0, 1) < 112_000


def test_reject_negative_weight():
    g = tiny_graph()
    g.add_edge('S', 'A', length=-1)
    with pytest.raises(ValueError):
        compute_route(g, 'S', 'T')
