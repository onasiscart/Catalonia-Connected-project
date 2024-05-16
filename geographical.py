from dataclasses import dataclass


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Zone:
    bottom_left: Point
    top_right: Point


# proposta del mòdul classes
