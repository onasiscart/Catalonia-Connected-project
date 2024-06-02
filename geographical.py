from dataclasses import dataclass
from haversine import haversine


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Zone:
    bottom_left: Point
    top_right: Point


def distance_between_points(start: Point, end: Point) -> float:
    """
    Returns the distance between two geographical points 'start' and 'end' in Km,
    taking into account the Earth's curvature
    """
    point1, point2 = (start.lat, start.lon), (end.lat, end.lon)
    return haversine(point1, point2)


def in_zone(box: Zone, coord: Point) -> bool:
    """
    returns True iff coord is inside the box
    """
    # we assume the box is small enough to not take the Earth's curvature into account
    return (
        box.bottom_left.lat <= coord.lat <= box.top_right.lat
        and box.bottom_left.lon <= coord.lon <= box.top_right.lon
    )
