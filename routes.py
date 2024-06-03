import simplekml
import networkx as nx
from geographical import Point, distance_between_points
from dataclasses import dataclass
from monuments import Monuments
from staticmap import *
from viewer import display_map


@dataclass
class Route:
    total_dist: float
    start: Point
    end: Point  # coordinates of the endpoint of the routes (corresponds to "coord" attribute of a node in the graph)
    path: list[Point]  # list of points (nodes in the graph) visited
      

Routes = list[Route]


def search_for_closest_node(graph: nx.Graph, point: Point) -> int:
    """
    Returns the closest node to the point.
    Pre: all nodes are integers and have a "coord" attribute
    """
    min_dist, closest_node = -1.0, 0
    for node in graph.nodes():
        # check types
        point2 = graph.nodes[node]["coord"]
        distance = distance_between_points(point, point2)
        if distance < min_dist or min_dist == -1.0:
            min_dist, closest_node = distance, node
    return closest_node


def assign_monuments(graph: nx.Graph, endpoints: Monuments) -> None:
    """
    Assign each monument to its closest point in the graph.
    Pre: all nodes in the graph have an attribute "monuments"
    """
    for monument in endpoints:
        closest_node = search_for_closest_node(graph, monument.location)
        graph.nodes[closest_node]["monuments"].append(monument)
        

def compute_total_distance(graph: nx.Graph, path: list[int]) -> float:
    """
    Computes the total lenght (sum of weights) of the path (list of nodes) in the weighted graph 'graph'.
    """
    return sum(graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))


def find_shortest_routes(graph: nx.Graph, start: int) -> Routes:
    """
    Find the shortest routes from the start point to each monument on the graph.
    """
    targets = [node for node in graph.nodes() if graph.nodes[node]["monuments"]]
    routes = []
    # use dijkstra's algorithm to find shortest paths from start to each node containig monuments
    for target in targets:
        try:
            path = nx.dijkstra_path(graph, source=start, target=target, weight="weight")
            start_point: Point = graph.nodes[start]["coord"]
            endpoint: Point = graph.nodes[target]["coord"]
            point_path: list[Point] = [graph.nodes[node]["coord"] for node in path]
            routes.append(
                Route(
                    compute_total_distance(graph, path),
                    start_point,
                    endpoint,
                    point_path,
                )
            )
        # it could be that we cannot reach a certain monument
        except nx.NetworkXNoPath:
            print(
                f"There's no path between your starting point and {graph.nodes[target]['monuments'][0].name}"
            )
    return routes


def find_routes(graph: nx.Graph, start: Point, endpoints: Monuments) -> Routes:
    """
    Find the shortest routes between the starting point "start" and all the endpoints.
    """
    assign_monuments(graph, endpoints)
    return find_shortest_routes(graph, search_for_closest_node(graph, start))


def export_routes_PNG(routes: Routes, filename: str) -> None:
    """
    Export the graph to a PNG file using staticmap.
    """
    map = StaticMap(800, 600)
    # mark the starting point in red only once (all routes start there)
    start_marker = CircleMarker((routes[0].start.lon, routes[0].start.lat), "red", 8)
    for route in routes:
        # mark the monuments in purple
        end_marker = CircleMarker((route.end.lon, route.end.lat), "purple", 8)
        map.add_marker(start_marker)
        map.add_marker(end_marker)
        # add routes to the map
        if route.path:
            line = Line(
                [(point.lon, point.lat) for point in route.path],
                "deeppink",
                width=2,
            )
            map.add_line(line)
    # save and display the map
    map.render().save(filename)
    display_map(filename)


def export_routes_KML(routes: Routes, filename: str) -> None:
    """
    Export the routes to a KML file named "filename".
    """
    kml = simplekml.Kml()
    # mark starting point only once (all routes start there)
    start_point = kml.newpoint(
        name="Start Point", coords=[(routes[0].start.lon, routes[0].start.lat)]
    )
    for route in routes:
        # mark endpoint of each route
        end_point = kml.newpoint(
            name="End point", coords=[(route.end.lon, route.end.lat)]
        )
        # add routes
        linestring = kml.newlinestring()
        linestring.coords = [(point.lon, point.lat) for point in route.path]
        linestring.style.linestyle.color = simplekml.Color.rgb(254, 130, 140)
        linestring.style.linestyle.width = 3
        linestring.name = f"Route from ({route.start.lat}, {route.start.lon}) to ({route.end.lat}, {route.end.lon})"
        linestring.description = f"Total Distance: {route.total_dist} km"
    # save the map
    kml.save(filename)
