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




def simplify_graph(graph: nx.Graph, epsilon: float) -> nx.Graph:
    """Simplify the graph."""




def get_graph(segments: Segments, clusters: int, epsilon: float) -> nx.Graph:
    G = make_graph(segments, clusters)
    simplified = simplify_graph(G, epsilon)
    weighted_G = add_weights(simplified)
    return weighted_G
    



