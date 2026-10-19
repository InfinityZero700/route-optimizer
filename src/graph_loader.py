"""Download OSM street data using OSMnx, retaining routable components."""
import networkx as nx


def load_street_network(place='Bellevue, Washington, USA', network_type='drive'):
    try:
        import osmnx as ox
    except ImportError as exc:
        raise RuntimeError('Install requirements first: pip install -r requirements.txt') from exc
    graph = ox.graph_from_place(place, network_type=network_type)
    if len(graph) == 0:
        raise ValueError(f'No road network returned for {place!r}')
    if not nx.is_strongly_connected(graph):
        nodes = max(nx.strongly_connected_components(graph), key=len)
        graph = graph.subgraph(nodes).copy()
    return graph
