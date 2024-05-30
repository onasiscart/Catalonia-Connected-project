import simplekml
import networkx as nx
from geographical import Point
from dataclasses import dataclass
from haversine import haversine
from monuments import Monuments
from staticmap import *
from viewer import display_map


@dataclass
class Route:
    total_dist: float # distància total de la ruta
    start: Point
    end: Point      # punt del node on acaba la ruta, contindrà un monument
    path: list[Point] # llista de nodes per on passem


Routes = list[Route]


def euclidean_distance(coord1: Point, coord2: Point) -> float:
    """"""
    return (coord1.lat - coord2.lat)**2 + (coord1.lon - coord2.lon)**2


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


def search_for_closest_node2(graph: nx.Graph, coord: Point) -> int:
    """
    returns the closest node to the point 'location'.
    """
    min_dist, closest_node = -1, 0
    for node in graph.nodes():
        point = (graph.nodes[node]['coord'].lat, graph.nodes[node]['coord'].lon)
        distance = haversine((coord.lat, coord.lon), point)
        if distance < min_dist or min_dist == -1:
            min_dist, closest_node = distance, node
    return closest_node


def assign_monuments(graph: nx.Graph, endpoints: Monuments) -> None:
    """
    Assign each monument to its closest point in the graph. 
    """
    for monument in endpoints:
        closest_node = search_for_closest_node2(graph, monument.location)
        graph.nodes[closest_node]["monuments"].append(monument)  # type:ignore
        # aquí dalt no sé per què fallen els tipus


def _compute_total_lenght(graph: nx.Graph, path: list[int]) -> float: 
    """
    computes the total lenght of the path 'path' in the weighted graph 'graph'.
    """
    return sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))


def find_shortest_routes(graph: nx.Graph, location: int) -> Routes:  # no entenc què és routes
    """
    Find the shortest routes from the location point to each monument on the graph. 
    """
    targets = [node for node in graph.nodes() if graph.nodes[node]['monuments']]
    routes = []
    
    for target in targets:
        try:
            path = nx.dijkstra_path(graph, source = location, target = target, weight = 'weight')
            start_point: Point = graph.nodes[location]['coord']
            endpoint: Point = graph.nodes[target]['coord']
            point_path: list[Point] = [graph.nodes[node]['coord'] for node in path]
            routes.append(Route(_compute_total_lenght(graph, path), start_point, endpoint, point_path))

        except nx.NetworkXNoPath:
            print(f"There's no path between your starting point and {graph.nodes[target]['monuments'][0].name}")

    return routes


def find_routes(graph: nx.Graph, location: Point, endpoints: Monuments) -> Routes:
    """
    Find the shortest route between the starting point and all the endpoints.
    graph és el graf que rebem de graphmaker, o sigui, el clusteritzat i simplificat
    però sense els monuments assignats.
    """
    assign_monuments(graph, endpoints)
    return find_shortest_routes(graph, search_for_closest_node2(graph, location))


def export_routes_PNG(routes: Routes, filename: str) -> None:
    """
    Export the graph to a PNG file using staticmap. 
    """
    map = StaticMap(800, 600)
    for route in routes:
        start_marker = CircleMarker((route.start.lon, route.start.lat), 'green', 8)
        end_marker = CircleMarker((route.end.lon, route.end.lat), 'red', 8)
        
        map.add_marker(start_marker)
        map.add_marker(end_marker)
        
        if route.path:
            line = Line([(point.lon, point.lat) for point in route.path], 'blue', 2)
            map.add_line(line)
    
    map.render().save(filename)
    display_map(filename)


def export_routes_KML(routes: Routes, filename: str) -> None:
    """
    Export the routes to a KML file.
    """
    kml = simplekml.Kml()

    for route in routes:
        linestring = kml.newlinestring()
        linestring.coords = [(point.lon, point.lat) for point in route.path]
        linestring.style.linestyle.color = simplekml.Color.red
        linestring.style.linestyle.width = 3
        linestring.name = f"Route from ({route.start.lat}, {route.start.lon}) to ({route.end.lat}, {route.end.lon})"
        linestring.description = f"Total Distance: {route.total_dist} km"

    kml.save(filename)
