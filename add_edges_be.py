def add_edges(graph: nx.Graph, point_labels: ndarray) -> None:
    """"""
    segment_count: dict[tuple[int, int], int] = {}  # ((u,v), nombre de segments)
    for i in range(0, len(point_labels), 2):
        p1cluster, p2cluster = point_labels[i], point_labels[i + 1]
        if p1cluster != p2cluster:
            edge = (min(p1cluster, p2cluster), max(p1cluster, p2cluster))
            if edge in segment_count:
                segment_count[edge] += 1
            else:
                segment_count[edge] = 1
            # now we check if we can add an edge to the graph
            if segment_count[edge] > MIN_SEGMENTS:
                graph.add_edge(
                    p1cluster,
                    p2cluster,
                    weight=distance_between_nodes(
                        graph.nodes[p1cluster]["coord"], graph.nodes[p2cluster]["coord"]
                    ),
                )
