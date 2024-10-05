import networkx as nx
from staticmap import *
import simplekml
import platform
import subprocess
import os


def display_map(filename: str) -> None:
    """
    Automatically opens the PNG file 'filename' containing a map
    """
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filename])
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", filename])


def export_graph_PNG(graph: nx.Graph, filename: str) -> None:
    """
    Export a networkx graph to a PNG file "filename" using staticmap.
    Pre: all nodes of the graoh have a "coord" attribute
    """
    static_map = StaticMap(width=800, height=600)
    # Iterate over nodes and add them to the map
    for node in graph.nodes():
        lat = graph.nodes[node]["coord"].lat  # typeerror!!!
        lon = graph.nodes[node]["coord"].lon
        marker = CircleMarker((lon, lat), "royalblue", 5)
        static_map.add_marker(marker)
    # Iterate over edges and add them to the map
    for u, v in graph.edges():
        lat1, lon1 = graph.nodes[u]["coord"].lat, graph.nodes[u]["coord"].lon
        lat2, lon2 = graph.nodes[v]["coord"].lat, graph.nodes[v]["coord"].lon
        line = Line([(lon1, lat1), (lon2, lat2)], "royalblue", width=2)
        static_map.add_line(line)
    # Save and display the map as an image
    static_map.render().save(filename)
    display_map(filename)


def export_graph_KML(graph: nx.Graph, filename: str) -> None:
    """
    Export a networkx graph to a KML file "filename".
    Pre: all nodes have a "coord" attribute
    """
    kml = simplekml.Kml()
    # iterate over edges and add them to the graph
    for u, v in graph.edges():
        u_lon, u_lat = graph.nodes[u]["coord"].lat, graph.nodes[u]["coord"].lon
        v_lon, v_lat = graph.nodes[v]["coord"].lat, graph.nodes[v]["coord"].lon
        line = kml.newlinestring(
            name=f"{u} to {v}", coords=[(u_lat, u_lon), (v_lat, v_lon)]
        )
        line.style.linestyle.color = simplekml.Color.rgb(
            173, 216, 230
        )  # light blue colour
    # save the .kml file
    kml.save(filename)
