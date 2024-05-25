from monuments1 import *
import networkx as nx
from graphmaker import *
from geographical import *
import math
import simplekml
from staticmap import *
from typing import TypeAlias


class Route:
    """
    Segons el que sembla en les funcions export, routes és un graf o una llista de rutes.
    Més o menys hauria de tenir aquests atributs
    """

    total_dist: int  # distància total de la ruta
    start: Point
    end: Monument  # monument on acaba la ruta o potser millor tots els monuments
    path: list[Point]  # llista de nodes per on passem


Routes: TypeAlias = list[Route]


def distance(coord1: Point, coord2: Point) -> float:
    """"""


def search_for_closest_node(endpoint: Point, graph: nx.Graph) -> int:
    """
    retorna índex del node del graf amb atribuvt "coords" més proper al endpoint (coordenades cartesianes)
    Prec: tots els nodes del graf tenen un atribut "coords"
    """
    # no hem trobat millor manera que no sigui recórrer tot el graf
    min_dist = math.inf
    closest_node = -1
    for node_id, attributes in graph.nodes():  # type: ignore
        # aquí dalt no sé com solucionar l'error de tipus!
        dist = distance(endpoint, attributes["coord"])
        if dist < min_dist:
            min_dist = dist
            closest_node = node_id
    return closest_node


def assign_monuments(graph: nx.Graph, endpoints: Monuments) -> None:
    """
    Assign each monument to its closest point in the graph. Networkx lets you
    assing aribtrary data to a node
    """
    # mirarem per cada monument tots els nodes del graph, a veure quin està a distància menor
    for monument in endpoints:
        closest_node = search_for_closest_node(monument.location, graph)
        # if ja tenim monuments, sinó l'hem de crear!
        graph[closest_node]["monuments"].append(monument)  # type:ignore
        # aquí dalt no sé per què fallen els tipus


def find_shortest_routes(
    graph: nx.Graph,
) -> Routes:  # no entenc bé què es routes
    """
    Find the shortest routes to each monument on the graph. Netxorkx has a funtion
    to find the mst from a nx.Graph
    """
    ...


def find_routes(graph: nx.Graph, start: Point, endpoints: Monuments) -> Routes:
    """
    Find the shortest route between the starting point and all the endpoints.
    graph és el graf que rebem de graphmaker, o sigui, el clusteritzat i simplificat
    però sense els monuments assignats.
    """
    assign_monuments(graph, endpoints)
    return find_shortest_routes(graph)


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


def export_PNG(routes: Routes, filename: str) -> None:
    """Export the graph to a PNG file using staticmap. Segons la capçalera, enten que
    routes ha de ser un graf??"""
    # Create a StaticMap object
    static_map = StaticMap(width=800, height=600)
    # add start point marker, since all routes start from the same point
    start_marker = CircleMarker((routes[0].start.lon, routes[0].start.lat), "blue", 10)
    static_map.add_marker(start_marker)
    for route in routes:
        # Create a Line object to represent the route path
        line = Line(((point.lon, point.lat) for point in route.path), "red", 3)
        static_map.add_line(line)
        # Add end markers
        end_marker = CircleMarker((route.end.lon, route.end.lat), "green", 10)
        static_map.add_marker(end_marker)
    # Save the map as an image
    static_map.render().save(filename)
    _display_map(filename)


def export_KML(routes: Routes, filename: str) -> None:
    """Export the graph to a KML file."""
    kml = simplekml.Kml()
    for route in routes:
        # Create a LineString representing the route path
        linestring = kml.newlinestring(
            name=f"Route: {route.start.name} to {route.end.name}",
            description=f"Total distance: {route.total_dist}",
            coords=[(point.lon, point.lat) for point in route.path],
        )

        # Add start and end points as placemarks
        kml.newpoint(
            name=f"Start: {route.start.name}",
            coords=[(route.start.lon, route.start.lat)],
        )
        kml.newpoint(
            name=f"End: {route.end.name}", coords=[(route.end.lon, route.end.lat)]
        )
    # Save the KML to a file
    kml.save(filename)
