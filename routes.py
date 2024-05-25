import simplekml
import networkx as nx
from geographical import Point
from typing import TypeAlias
from dataclasses import dataclass
from haversine import haversine
import math
from staticmap import *
from viewer import display_map


@dataclass
class Monument:
    name: str
    location: Point


Monuments: TypeAlias = list[Monument]


@dataclass
class Route:
    total_dist: float # distància total de la ruta
    start: Point
    end: Point      # punt del node on acaba la ruta, contindrà un monument
    path: list[Point] # llista de nodes per on passem

Routes = list[Route]


def distance(coord1: Point, coord2: Point) -> float:
    """"""


# def search_for_closest_node(graph: nx.Graph, endpoint: Point) -> int:
#     """
#     retorna índex del node del graf amb atribut "coords" més proper al endpoint (coordenades cartesianes)
#     Prec: tots els nodes del graf tenen un atribut "coords"
#     """
#     # no hem trobat millor manera que no sigui recórrer tot el graf
#     min_dist = math.inf
#     closest_node = -1
#     for node_id, attributes in graph.nodes():  # type: ignore
#         # aquí dalt no sé com solucionar l'error de tipus!
#         dist = distance(endpoint, attributes["coord"])
#         if dist < min_dist:
#             min_dist, closest_node = dist, node_id
#     return closest_node


def search_for_closest_node2(graph: nx.Graph, start: Point) -> int:
    """
    returns the closest node to the starting point requested by the user. LINEAR TIME!!
    """
    min_dist, closest_node = -1, 0
    for node in graph.nodes():
        point = (graph.nodes[node]['coord'].lat, graph.nodes[node]['coord'].lon)
        distance = haversine((start.lat, start.lon), point)
        if distance < min_dist or min_dist == -1:
            min_dist, closest_node = distance, node
    print('closest node:', closest_node)
    return closest_node


def assign_monuments(graph: nx.Graph, endpoints: Monuments) -> None:
    """
    Assign each monument to its closest point in the graph. 
    """
    for monument in endpoints:
        closest_node = search_for_closest_node2(graph, monument.location)
        print('info del closest:', graph[closest_node])
        graph[closest_node]["monuments"].append(monument)  # type:ignore
        print('i assigned', monument,'to', closest_node)
        # aquí dalt no sé per què fallen els tipus


def _compute_total_lenght(graph: nx.Graph, path: list[int]) -> float: 
    """
    computes the total lenght of the path 'path' in the weighted graph 'graph'.
    """
    return sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))


def find_shortest_routes(graph: nx.Graph, start: int) -> Routes:  # no entenc què és routes
    """
    Find the shortest routes from the start point to each monument on the graph. 
    """
    targets = [node for node in graph.nodes() if graph.nodes[node]['monuments'] != []]
    routes = []
    print('targets:', targets)

    for target in targets:
        try:
            path = nx.dijkstra_path(graph, source = start, target = target, weight = 'weight')
            start_point: Point = graph.nodes[start]['coord']
            endpoint: Point = graph.nodes[target]['coord']
            point_path: list[Point] = [graph.nodes[node]['coord'] for node in path]
            routes.append(Route(_compute_total_lenght(graph, path), start_point, endpoint, point_path))

        except nx.NetworkXNoPath:
            print(f"No path between {start} and {target}")

    return routes


def find_routes(graph: nx.Graph, start: Point, endpoints: Monuments) -> Routes:
    """
    Find the shortest route between the starting point and all the endpoints.
    graph és el graf que rebem de graphmaker, o sigui, el clusteritzat i simplificat
    però sense els monuments assignats.
    """
    assign_monuments(graph, endpoints)
    return find_shortest_routes(graph, search_for_closest_node2(graph, start))


def export_routes_PNG(routes: Routes, filename: str) -> None:
    """
    Export the graph to a PNG file using staticmap. Segons la capçalera, enten que
    routes ha de ser un graf??
    """
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

    static_map.render().save(filename)
    display_map(filename)


def export_routes_KML(routes: Routes, filename: str) -> None:
    """
    Export the graph to a KML file. Exportem les rutes a un fitxer KML. Podem fer un fitxer
    que contingui tant el graf com les rutes?
    """
    kml = simplekml.Kml()
    for route in routes:
        # Create a LineString representing the route path
        linestring = kml.newlinestring(
            name=f"Route: {route.start} to {route.end}",
            description=f"Total distance: {route.total_dist}",
            coords=[(point.lon, point.lat) for point in route.path],
        )

        # Add start and end points as placemarks
        kml.newpoint(
            name=f"Start: {route.start}",
            coords=[(route.start.lon, route.start.lat)],
        )
        kml.newpoint(
            name=f"End: {route.end}", coords=[(route.end.lon, route.end.lat)]
        )
    # Save the KML to a file
    kml.save(filename)
