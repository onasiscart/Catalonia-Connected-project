import requests
import os
import gpxpy
import staticmap
from haversine import haversine
from dataclasses import dataclass
from typing import TypeAlias
from datetime import datetime
from typing import Optional
from geographical import Point, Zone
from viewer import display_map


@dataclass
class Segment:
    start: Point
    end: Point


Segments: TypeAlias = list[Segment]

MAX_TIME = 100  # maximum time difference acceptable between two points red like xx : xx (min, sec)
MAX_DIST = 0.1  # maximum distance in Km acceptable between two points


def _distance_between_points(start: Point, end: Point) -> float:
    """
    Returns the distance between two geographical points 'start' and 'end' in Km
    """
    point1, point2 = (start.lat, start.lon), (end.lat, end.lon)
    return haversine(point1, point2)


def _format_date_and_time(time: Optional[datetime],) -> Optional[tuple[int, int]]:  # using optional because time can be None when downloading
    """
    Converts the string 'time_string'into a tuple which contains the date and time
    """
    if time != None:
        return (int(time.strftime("%Y%m%d")), int(time.strftime("%H%M%S")))
    return None


def _is_segment_valid(p1: Point, p2: Point, p1_time: datetime, p2_time: datetime) -> bool:
    """
    Returns a bool based on whether the segment 's' is valid for use or not.
    """
    time1, time2 = _format_date_and_time(time1), _format_date_and_time(time2)
    if time1 and time2:
        if time1[1] > time2[1]:
            return False
        elif (time2[1] - time1[1]) > MAX_TIME:
            return False
        elif time1[0] != time2[0]:
            return False
        elif _distance_between_points(p1, p2) > MAX_DIST:
            return False
        return True
    return False


def _download_segments(zone: Zone, filename: str) -> None:
    """
    Download all segments in thezone and save them to the file 'filename'.
    """
    p1, p2 = zone.bottom_left, zone.top_right
    zone_string = "{},{}, {},{}".format(p1.lat, p1.lon, p2.lat, p2.lon)

    page = 0
    with open(filename, "w") as file:
        while True:
            # zone a la url ha de ser un string de zone
            url = f"https://api.openstreetmap.org/api/0.6/trackpoints?bbox={zone_string}&page={page}"
            response = requests.get(url)
            gpx_content = response.content.decode("utf-8")
            gpx = gpxpy.parse(gpx_content)

            if len(gpx.tracks) == 0:
                break

            for track in gpx.tracks:
                for segment in track.segments:
                    if all(point.time is not None for point in segment.points):
                        segment.points.sort(key=lambda p: p.time)
                        for i in range(len(segment.points) - 1):
                            p1, p2 = segment.points[i], segment.points[i + 1]
                            point1 = Point(float(p1.latitude), float(p1.longitude))
                            point2 = Point(float(p2.latitude), float(p2.longitude))
                            if _is_segment_valid(point1, point2, p1.time, p2.time):
                                file.write(
                                    f"{p1.latitude}, {p1.longitude} - {p2.latitude}, {p2.longitude}\n"
                                )
            page += 1


def _load_segments(filename: str) -> Segments:
    """
    Loads segments from the file 'filename' and returns a list of segments.
    """
    segments: Segments = []
    with open(filename, "r") as file:
        for line in file:
            points_data = line.strip().split(" - ")
            point1_data, point2_data = points_data[0].split(", "), points_data[1].split(
                ", "
            )

            point1 = Point(
                float(point1_data[0]),
                float(point1_data[1]),
            )
            point2 = Point(
                float(point2_data[0]),
                float(point2_data[1]),
            )
            segments.append(Segment(point1, point2))
    return segments


def get_segments(zone: Zone, filename: str) -> Segments:
    """
    Get all cleaned data of the segments in the box.If filename exists, load segments
    from the file. Otherwise, download segments in the box and save them to the file.
    """
    if not os.path.exists(filename):
        _download_segments(zone, filename)
    return _load_segments(filename)


def show_segments(segments: Segments, filename: str) -> None:
    """
    Show all segments in a PNG file using staticmap.
    """
    static_map = staticmap.StaticMap(800, 600)
    for segment in segments:
        line = staticmap.Line(
            [
                (segment.start.lon, segment.start.lat),
                (segment.end.lon, segment.end.lat),
            ],
            color="black",
            width=1,
        )
        static_map.add_line(line)
    static_map.render().save(
        filename, format="png"
    )  # no serveix de res poasr el fromat aquí, cal indicar-ho al cridar la funció amb
    display_map(filename)  # un nom filename.png


if __name__ == '__main__':
    pass
