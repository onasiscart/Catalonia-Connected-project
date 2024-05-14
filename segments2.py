import os
import gpxpy
import requests
import platform
import staticmap
import subprocess
from typing import TypeAlias
from datetime import datetime
from dataclasses import dataclass
from haversine import haversine


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Segment:
    start: Point
    end: Point


class Zone:
    """
    indicates the top-right and bottom-left coordinates of the points
    in a rectangular zone
    """

    bottom_left: Point
    top_right: Point


Segments: TypeAlias = list[Segment]
Time = tuple[int, int]  # date and time

MAX_TIME = 100  # maximum time difference acceptable between two points red like xx : xx (min, sec)
MAX_DIST = 0.1  # maximum distance in Km acceptable between two points


def _download_segments(zone: Zone, filename: str) -> None:
    """
    Download all segments in thezone and save them to the file 'filename'.
    """
    page = 0
    with open(filename, "w") as file:
        while True:
            url = f"https://api.openstreetmap.org/api/0.6/trackpoints?bbox={zone}&page={page}"
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
                            file.write(
                                f"{p1.latitude}, {p1.longitude}, {p1.time} - {p2.latitude}, {p2.longitude}, {p2.time}\n"
                            )
            page += 1


def length_of_a_segment(start: Point, end: Point) -> float:
    """
    Returns the distance between two geographical points 'start' and 'end' in Km
    """
    return haversine((start.lat, start.lon), (end.lat, end.lon))


def _is_segment_valid(segment: Segment, time: tuple[Time, Time]) -> bool:
    """
    Returns a bool based on whether the segment 's' is valid for use or not.
    """
    if time[1][1] > time[1][1]:
        return False
    elif (time[1][1] - time[0][1]) > MAX_TIME:
        return False
    elif time[0][0] != time[1][0]:
        return False
    elif length_of_a_segment(segment.start, segment.end) > MAX_DIST:
        return False
    return True


def _clean_segment_data(data: tuple[Segments, list[tuple[Time, Time]]]) -> Segments:
    """
    Deletes all defective segments from the list 'segments'.
    """
    segments, times = data
    endpoint, errors = len(segments) - 1, 0
    for i in range(endpoint):
        if not _is_segment_valid(segments[i], times[i]):
            segments[endpoint - errors], segments[i] = (
                segments[i],
                segments[endpoint - errors],
            )
            times[endpoint - errors], times[i] = (
                times[i],
                times[endpoint - errors]
            )
            errors += 1
    for _ in range(errors):
        segments.pop()
    return segments


def _format_date_and_time(time_string: str) -> tuple[int, int]:
    """
    Converts the string 'time_string'into a tuple which contains the date and time.
    """
    time = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S%z")
    return (int(time.strftime("%Y%m%d")), int(time.strftime("%H%M%S")))


def _load_segments(filename: str) -> tuple[Segments, list[tuple[Time, Time]]]:
    """
    Loads segments from the file 'filename' and returns a list of segments.
    """
    segments: Segments = []
    times: list[tuple[int, int]] = []
    with open(filename, "r") as file:
        for line in file:
            points_data = line.strip().split(" - ")
            point1_data = points_data[0].split(", ")
            point2_data = points_data[1].split(", ")

            point1 = Point(
                float(point1_data[0]),
                float(point1_data[1]),
            )
            point2 = Point(
                float(point2_data[0]),
                float(point2_data[1]),
            )
            segments.append(Segment(point1, point2))
            times.append(
                (
                    _format_date_and_time(str(point1_data[2])),
                    _format_date_and_time(str(point2_data[2])),
                )
            )
    return (segments, times)


def file_exists(filename: str) -> bool:
    """
    Returns True iff the filename exists in the current working directory
    """
    return os.path.exists(filename)


def get_segments(zone: Zone, filename: str) -> Segments:
    """
    Get all cleaned data of the segments in the box.If filename exists, load segments
    from the file. Otherwise, download segments in the box and save them to the file.
    """
    if not file_exists(filename):
        _download_segments(zone, filename)
    return _clean_segment_data(_load_segments(filename))


def _display_segments_map(filename: str) -> None:
    """
    Automatically opens the PNG file 'filename' containing the map of segments
    """
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filename])
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", filename])


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
    _display_segments_map(filename)  # un nom filename.png
