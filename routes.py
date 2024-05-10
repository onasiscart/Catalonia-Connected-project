import networkx as nx
from segments import Point
from typing import TypeAlias
from dataclasses import dataclass


@dataclass
class Monument:
    name: str
    location: Point


Monuments: TypeAlias = list[Monument]


class Routes:
    """
    no tinc ni idea de com implementar o per què servirà routes però més o menys entenc això.
    Potser routes hauria de ser una llista de Route, que sí tindria aquests atributs. Segons el que
    sembla en les funcions export, routes és un graf o una llista de rutes
    """
    total_dist: int  # distància total de la ruta
    start: Point
    end: Monument  # monument on acaba la ruta
    path: list[Point]  # llista de nodes per on passem


def assign_monuments(graph: nx.Graph, endpoints: Monuments) -> None:
    """
    Assign each monument to its closest point in the graph. Networkx lets you
    assing aribtrary data to a node
    """
    ...


def find_shortest_routes(graph: nx.Graph,) -> Routes:  # no entenc què es routes
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


def export_PNG(routes: Routes, filename: str) -> None:
    """Export the graph to a PNG file using staticmap. Segons la capçalera, enten que
    routes ha de ser un graf??"""
    ...


def export_KML(groutes: Routes, filename: str) -> None:
    """Export the graph to a KML file."""
    ...
