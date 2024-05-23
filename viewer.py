import networkx as nx
from staticmap import *
import simplekml
import platform
import subprocess
import os

def _display_map(filename: str) -> None:
    """
    Automatically opens the PNG file 'filename' containing the map of segments
    """
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filename])
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", filename])


def export_PNG(graph: nx.Graph, filename: str) -> None:
    """Export the graph to a PNG file using staticmap."""
    # Create a StaticMap object
    static_map = StaticMap(width=800, height=600)

    # Iterate over nodes and add them to the map
    for node in graph.nodes():
        lat = graph.nodes[node]["coord"].lat # es queixa pq no sap què guardem a ["coord"]
        lon = graph.nodes[node]["coord"].lon
        marker = CircleMarker((lon, lat), "red", 5)
        static_map.add_marker(marker)

    # Iterate over edges and add them to the map
    for u, v in graph.edges():
        lat1, lon1 = graph.nodes[u]["coord"].lat, graph.nodes[u]["coord"].lon
        lat2, lon2 = graph.nodes[v]["coord"].lat, graph.nodes[v]["coord"].lon
        line = Line([(lon1, lat1), (lon2, lat2)], "blue", 2)
        static_map.add_line(line)

    # Save the map as an image
    static_map.render().save(filename)
    _display_map(filename)


def export_KML(graph: nx.Graph, filename: str) -> None:
    """Export the graph to a KML file."""
    kml = simplekml.Kml()

    # Add nodes to the KML
    # for node in graph.nodes():
    #     lon = graph.nodes[node]["coord"].lat
    #     lat = graph.nodes[node]["coord"].lon
    #     kml.newpoint(name=str(node), coords=[(lat, lon)])

    # Add edges to the KML
    for u, v in graph.edges():
        u_lon, u_lat = graph.nodes[u]["coord"].lat, graph.nodes[u]["coord"].lon
        v_lon, v_lat = graph.nodes[v]["coord"].lat, graph.nodes[v]["coord"].lon
        line = kml.newlinestring(
            name=f"{u} to {v}", coords=[(u_lat, u_lon), (v_lat, v_lon)]
        )
        line.style.linestyle.color = (
            simplekml.Color.blue
        )  # Change the edge color if needed

    # Save the KML to a file
    kml.save(filename)
