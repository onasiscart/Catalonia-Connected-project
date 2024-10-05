import networkx as nx
from typing import TypeAlias
from numpy import ndarray
import numpy as np
from sklearn.cluster import KMeans
from segments import *
from math import acos
from geographical import Point, distance_between_points


MIN_SEGMENTS = 0  # minimum number of segments that must connect two nodes in order to create an edge between them


Edge: TypeAlias = tuple[int, int]  # [centroid1_number, centroid2_number]


def modify_for_kmeans(segments: Segments) -> ndarray:  # type:ignore
    """
    Modifies a list of segments "segments" to a numpy array so that it can be input into a kmeans clustering algorithm
    """
    points = np.array(
        [
            [point.lat, point.lon]
            for segment in segments
            for point in [segment.start, segment.end]
        ]
    )
    return points

  
def add_nodes(graph: nx.Graph, centroid_coords: ndarray) -> None:
    """
    given a graph and a list of coordinates, adds nodes to the graph. Nodes will have the centroid number
    (centroid_coords index) as their name and a Point with their coordinates as an attribute
    Prec: the graph is empty
    """
    for centroid, coords in enumerate(centroid_coords):
        graph.add_node(
            centroid, coord=Point(float(coords[0]), float(coords[1])), monuments=[]
        )
        
        
def add_edges(graph: nx.Graph, point_labels: ndarray) -> None:
    """
    Adds edges to the graph, using point-labels (a list containing the cluster each point was assigned to)
    to check that there is enough "segments" between two nodes before adding an edge.
    """
    segment_count: dict[tuple[int, int], int] = {}  # ((u,v), nombre de segments)
    # the points in positions 0-1 were a segment, as were those in 2-3, 4-5, etc.
    # thus, we will check for segments between clusters by traversing the list 2 by 2
    for i in range(0, len(point_labels), 2):
        p1cluster, p2cluster = point_labels[i], point_labels[i + 1]
        # if two points joined by a segment were assigned to different clusters, we add a segment between clusters
        if p1cluster != p2cluster:
            edge = (min(p1cluster, p2cluster), max(p1cluster, p2cluster))
            if edge in segment_count:
                segment_count[edge] += 1
            else:
                segment_count[edge] = 1
            # if there are enough segments between clusters, we add an edge
            if segment_count[edge] > MIN_SEGMENTS:
                graph.add_edge(
                    p1cluster,
                    p2cluster,
                    weight=distance_between_points(
                        graph.nodes[p1cluster]["coord"], graph.nodes[p2cluster]["coord"]
                    ),
                )


def make_graph(segments: Segments, numclusters: int) -> nx.Graph:  # type:ignore
    """
    Make a graph(V, E) with V a set of "numclusters" nodes which are the result of a clustering of the points in
    segments, and E a set of edges indicating that there are segments joining the points in each cluster.
    Pre: segments is not empty, numclusters is positive
    """
    # 1. clustering
    # modify segments so it can be fit into a kmeans clustering algorithm
    points = modify_for_kmeans(segments)
    kmeans = KMeans(n_clusters=numclusters)
    kmeans.fit(points)
    centroid_coords = kmeans.cluster_centers_
    point_labels = kmeans.labels_
    # 2.create graph, add points and edges
    graph = nx.Graph()
    add_nodes(graph, centroid_coords)
    add_edges(graph, point_labels)
    return graph
  
  
def angle_between_points(p1: Point, p2: Point, p3: Point) -> float:
    """
    Returns the angle in degrees between three points p1 p2 and p3.
    """
    v1 = np.array([p2.lat - p1.lat, p2.lon - p1.lon])
    v2 = np.array([p2.lat - p3.lat, p2.lon - p3.lon])
    angle_rad = acos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return np.degrees(angle_rad)

  
def simplify_edge(graph: nx.Graph, n1: int, n2: int, n3: int) -> None:
    """
    Given a graph and three adjacent nodes n1, n2, n3, deletes the midpoint n2 and adds an edge
    between n1 and n3 with a weight = distance between the coordinates of n1 and n3.
    Pre: n1 and n3 are the only neighbours of n2
    """
    graph.remove_node(n2)
    graph.add_edge(
        n1,
        n3,
        weight=distance_between_points(
            graph.nodes[n1]["coord"], graph.nodes[n3]["coord"]
        ),
    )


def simplify_graph(graph: nx.Graph, epsilon: float) -> nx.Graph:
    """
    Simplifies the graph. If there is a node n1 of degree 2 (connected to n2 and n3) and the two edges that pass through it
    form an angle bigger than 180 - epsilon, we delete that node and add an edge between the two adjacent nodes.
    """
    for node in list(graph.nodes()):
        if graph.degree(node) == 2:
            neighbors = list(graph.neighbors(node))
            u, v = neighbors[0], neighbors[1]
            if (
                angle_between_points(
                    graph.nodes[u]["coord"],
                    graph.nodes[node]["coord"],
                    graph.nodes[v]["coord"],
                )
                > 180 - epsilon
            ):
                simplify_edge(graph, u, node, v)
    return graph


def get_graph(
    segments: Segments, clusters: Optional[int], epsilon: Optional[float]
) -> nx.Graph:
    """
    Returns a networkx graph made from the segments data clustered into a number "clusters" of clusters, with edges
    that form angles of no more than 180 - epsilon degrees.
    """
    if not clusters or not epsilon:
        clusters, epsilon = 100, 30
    return simplify_graph(make_graph(segments, clusters), epsilon)
