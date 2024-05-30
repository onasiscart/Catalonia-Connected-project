import networkx as nx
from typing import TypeAlias
from numpy import ndarray
import numpy as np
from sklearn.cluster import KMeans
from segments import *
from haversine import haversine
from math import acos
from geographical import Point


# TO DO:
# nombre mínim de segments per posar una aresta

MIN_SEGMENTS = 0 # minimum number of segments that must connect two nodes in order to create an edge between them


Edge: TypeAlias = tuple[int, int]  # edges will be between centroids


def modify_for_kmeans(segments: Segments) -> ndarray:  # type:ignore
    points = np.array(
        [
            [point.lat, point.lon]
            for segment in segments
            for point in [segment.start, segment.end]
        ]
    )
    return points


def distance_between_nodes(coord1: Point, coord2: Point) -> float:
    """"""
    point1, point2 = (coord1.lat, coord1.lon), (
        coord2.lat,
        coord2.lon,
    )  
    return haversine(point1, point2)


def add_nodes(graph: nx.Graph, centroid_coords: ndarray) -> None:
    """Prec: G is empty"""
    for cluster, coords in enumerate(centroid_coords):
        # nodes tenen el nombre de centroide com a nom i el Point amb les seves coordenades com a atribut
        graph.add_node(cluster, coord=Point(float(coords[0]), float(coords[1])), monuments=[])


def add_edges(graph: nx.Graph, point_labels: ndarray) -> None:
    """
    Adds edges to the graph.
    """
    for i in range(0, len(point_labels), 2):
        p1cluster, p2cluster = point_labels[i], point_labels[i + 1]
        if p1cluster != p2cluster:
            graph.add_edge(
                p1cluster,
                p2cluster,
                weight=distance_between_nodes(
                    graph.nodes[p1cluster]["coord"], graph.nodes[p2cluster]["coord"]
                ),
            )


def make_graph(segments: Segments, clusters: int) -> nx.Graph:  # type:ignore
    """Make a graph from the segments."""
    # 1. clustering
    # modifiquem segments perquè pugui ser entrat a kmeans
    points = modify_for_kmeans(segments)  # type:ignore
    kmeans = KMeans(n_clusters=clusters)  # type:ignore
    kmeans.fit(points)
    # 2. creem el graf
    graph = nx.Graph()
    centroid_coords = kmeans.cluster_centers_
    point_labels = kmeans.labels_
    add_nodes(graph, centroid_coords)
    add_edges(graph, point_labels)
    return graph


def _angle_between_points(p1: Point, p2: Point, p3: Point) -> float:
    """
    returns the angle in degrees between three points p1 p2 and p3.
    """
    v1 = np.array([p2.lat - p1.lat, p2.lon - p1.lon])
    v2 = np.array([p2.lat - p3.lat, p2.lon - p3.lon])
    angle_rad = acos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return np.degrees(angle_rad)


def _update_segments(graph: nx.Graph, n1: int, n2: int, n3: int) -> None:
    """
    updates the segments of the graph, that is, deletes the mid-point from (n1 n2 n3)
    and updates their distance.
    """
    graph.remove_node(n2)
    graph.add_edge(n1, n3, weight = distance_between_nodes(graph.nodes[n1]["coord"], graph.nodes[n3]["coord"]))


def simplify_graph(graph: nx.Graph, epsilon: float) -> nx.Graph:
    """
    Simplifies the graph.
    """
    for node in list(graph.nodes()):
        if graph.degree(node) == 2:
            neighbors = list(graph.neighbors(node))
            u, v = neighbors[0], neighbors[1]
            if _angle_between_points(graph.nodes[u]["coord"], graph.nodes[node]["coord"], graph.nodes[v]["coord"]) > epsilon:
                _update_segments(graph, u, node, v)
    return graph


def get_graph(segments: Segments, clusters: Optional[int], epsilon: Optional[float]) -> nx.Graph:
    if not clusters or not epsilon:
        clusters, epsilon = 100, 30
    return simplify_graph(make_graph(segments, clusters), epsilon)


# def get_not_simplified(segments: Segments, clusters: Optional[int], epsilon: Optional[float]) -> nx.Graph:
#     return make_graph(segments, clusters)


# def get_not_simplified(segments: Segments, clusters: Optional[int], epsilon: Optional[float]) -> nx.Graph:
#     return make_graph(segments, clusters)
