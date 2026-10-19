"""Compare Dijkstra and A* on a drivable OpenStreetMap road network."""
import argparse
import csv
from pathlib import Path
import random
import statistics
import time

import networkx as nx

from src.graph_loader import load_street_network
from src.router import compute_route


def measure(graph, start, goal, algorithm):
    t0 = time.perf_counter()
    result = compute_route(graph, start, goal, algorithm)
    ms = (time.perf_counter() - t0) * 1000
    return result, ms


def save_map(graph, path, output):
    import folium
    coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in path]
    visual = folium.Map(location=coords[len(coords) // 2], zoom_start=13)
    folium.PolyLine(coords, color='royalblue', weight=5).add_to(visual)
    folium.Marker(coords[0], tooltip='Start').add_to(visual)
    folium.Marker(coords[-1], tooltip='Destination').add_to(visual)
    visual.fit_bounds(coords)
    visual.save(str(output))


def save_plot(rows, output):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    d = [r['dijkstra_nodes'] for r in rows]
    a = [r['astar_nodes'] for r in rows]
    ax.bar(['Dijkstra', 'A*'], [statistics.mean(d), statistics.mean(a)])
    ax.set_ylabel('Mean nodes explored')
    ax.set_title(f'Mean search effort over {len(rows)} route(s)')
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--place', default='Bellevue, Washington, USA')
    parser.add_argument('--pairs', type=int, default=10, help='Random origin/destination pairs')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--out', default='outputs')
    args = parser.parse_args()
    if args.pairs < 1:
        parser.error('--pairs must be at least 1')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f'Downloading road network for {args.place} ...')
    graph = load_street_network(args.place)
    print(f'Loaded {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges')
    nodes = list(graph.nodes)
    if len(nodes) < 2:
        raise RuntimeError('Need at least two road intersections')
    rng = random.Random(args.seed)
    rows = []
    first_path = None
    for i in range(args.pairs):
        start, goal = rng.sample(nodes, 2)
        d, dt = measure(graph, start, goal, 'dijkstra')
        a, at = measure(graph, start, goal, 'astar')
        if not d.path or not a.path or abs(d.distance_m - a.distance_m) > max(1e-5, d.distance_m * 1e-7):
            raise AssertionError('Route cost mismatch: inspect edge weights / admissibility assumptions')
        if first_path is None:
            first_path = a.path
        rows.append({'pair': i + 1, 'start': start, 'goal': goal,
                     'distance_m': round(d.distance_m, 3), 'dijkstra_nodes': d.nodes_explored,
                     'astar_nodes': a.nodes_explored,
                     'dijkstra_ms': round(dt, 3), 'astar_ms': round(at, 3)})
        print(f"Pair {i + 1:>2}: {d.distance_m:>9.1f} m | Dijkstra {d.nodes_explored:>5} nodes | A* {a.nodes_explored:>5} nodes")
    with (out / 'benchmark_results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    save_plot(rows, out / 'benchmark_comparison.png')
    save_map(graph, first_path, out / 'route_comparison.html')
    d_avg = statistics.mean(r['dijkstra_nodes'] for r in rows)
    a_avg = statistics.mean(r['astar_nodes'] for r in rows)
    print(f'\nMean nodes: Dijkstra={d_avg:.1f}, A*={a_avg:.1f}; change={(a_avg / d_avg - 1) * 100:+.1f}%')
    print(f'Results saved to {out.resolve()}')


if __name__ == '__main__':
    main()
