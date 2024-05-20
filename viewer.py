import networkx as nx
from staticmap import *
import simplekml


def export_PNG(graph: nx.Graph, filename: str) -> None:
    """Export the graph to a PNG file using staticmap."""
    # Create a StaticMap object
    static_map = StaticMap(width=800, height=600)

    # Iterate over nodes and add them to the map
    for node in graph.nodes():
        lat, lon = graph.nodes[node][
            "coord"
        ]  # Assuming nodes have 'pos' attribute containing (lon, lat) coordinates
        marker = CircleMarker((lon, lat), "red", 5)
        static_map.add_marker(marker)

    # Iterate over edges and add them to the map
    for u, v in graph.edges():
        lat1, lon1 = graph.nodes[u]["coord"]
        lat2, lon2 = graph.nodes[v]["coord"]
        line = Line([(lon1, lat1), (lon2, lat2)], "blue", 2)
        static_map.add_line(line)

    # Save the map as an image
    image = static_map.render()
    image.save(filename)


def export_KML(graph: nx.Graph, filename: str) -> None:
    """Export the graph to a KML file."""
    kml = simplekml.Kml()

    # Add nodes to the KML
    for node, data in graph.nodes(data=True):
        lon, lat = data.get(
            "pos", (0, 0)
        )  # Assuming nodes have 'pos' attribute containing (lon, lat) coordinates
        kml.newpoint(name=str(node), coords=[(lon, lat)])

    # Add edges to the KML
    for u, v in graph.edges():
        u_lon, u_lat = graph.nodes[u]["pos"]
        v_lon, v_lat = graph.nodes[v]["pos"]
        line = kml.newlinestring(
            name=f"{u} to {v}", coords=[(u_lon, u_lat), (v_lon, v_lat)]
        )
        line.style.linestyle.color = (
            simplekml.Color.blue
        )  # Change the edge color if needed

    # Save the KML to a file
    kml.save(filename)
