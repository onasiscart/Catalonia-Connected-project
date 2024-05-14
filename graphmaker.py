import networkx as nx
from typing import TypeAlias
from segments import Point
...


Node: TypeAlias = tuple[int, Point]  # [node id, coordinates of the node]
Edge: TypeAlias = tuple[int, int]  # edges will be between centroids


def make_graph(segments: Segments, clusters: int) -> nx.Graph:
    """Make a graph from the segments."""
    #modifiquem segments perquè pugui ser entrat a kmeans
    ...
    #1. clustering
    cluster = KMeans(n_clusters = clusters, ...).fit(point_data)
    #2. creem el graf
    graph = nx.Graph()
    #2.afegim els nodes
    nodes: list[Node] = list(enumerate(kmeans.cluster_centers_))
    #3. afehim les arestes!




def _distance_between_points(p1: Point, p2: Point) -> float:
    point1, point2 = (p1.lat, p1.lon), (
        p2.lat,
        p2.lon,
    )  
    return haversine(point1, point2)


def _add_weights(graph: nx.Graph) -> nx.Graph:
    """
    Adds the wieghts (the distances) to the graph.
    """
    for u, v in graph.edges():
        graph[u][v]['weight'] =_distance_between_points(u, v)
    return graph


def _angle_between_points(p1: Point, p2: Point, p3: Point) -> int:
    """
    returns the angle in degrees between three points p1 p2 and p3.
    """
    v1 = np.array([p2.lat - p1.lat, p2.lon - p1.lon])
    v2 = np.array([p2.lat - p3.lat, p2.lon - p3.lon])
    angle_rad = acos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return np.degrees(angle_rad)


def _delete_mid_point(graph: nx.Graph, n1: Point, n2: Point, n3: Point) -> None:
    """
    deletes an unnecessary point 'n2' in the graph and adds an edge between 
    """
    graph.remove_node(n2)
    graph.add_edge(n1, n3)


def simplify_graph(graph: nx.Graph, epsilon: float = 15) -> nx.Graph:
    """Simplify the graph."""
    for node in graph:
        if nx.degree(node) == 2:
            v, u = nx.neighbors(node)
            if _angle_between_points(u, node, v) > epsilon:
                _delete_mid_point(graph, v, node, u)


def get_graph(segments: Segments, clusters: int, epsilon: float) -> nx.Graph:
    simplified = simplify_graph(make_graph(segments, clusters), epsilon)
    return _add_weights(simplified)
