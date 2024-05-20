import networkx as nx
from typing import TypeAlias
from numpy import ndarray
import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
from segments import *
import matplotlib.pyplot as plt
from haversine import haversine, Unit


@dataclass
class Point:
    lat: float
    lon: float


# TODO:
# solucionar el import numpy que no funciona i no sé per què
# afegir distàncies en afegir les arestes
# nombre mínim de segments per posar una aresta

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
    )  # format per les dobles assignacions????
    return haversine(point1, point2, unit=Unit.KILOMETERS)


def add_nodes(graph: nx.Graph, centroid_coords: ndarray) -> None:
    """Prec: G is empty"""
    for cluster, coords in enumerate(centroid_coords):
        # nodes tenen el nombre de centroide com a nom i el Point amb les seves coordenades com a atribut
        graph.add_node(cluster, coord=Point(float(coords[0]), float(coords[1])))


def add_edges(graph: nx.Graph, point_labels: ndarray) -> None:
    """"""
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
    add_edges(graph, point_labels, centroid_coords)
    return graph


def simplify_graph(graph: nx.Graph, epsilon: float) -> nx.Graph:
    """Simplify the graph."""


def get_graph(segments: Segments, clusters: int, epsilon: float) -> nx.Graph:
    G = make_graph(segments, clusters)
    simplified = simplify_graph(G, epsilon)
    return simplified
