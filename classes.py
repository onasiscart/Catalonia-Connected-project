from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class Point:
    lat: float
    lon: float
    time: tuple[int, int]  #date and time

@dataclass
class Segment:
    start: Point
    end: Point

class Zone:
    bottom_left: Point
    top_right: Point

Segments: TypeAlias = list[Segment]