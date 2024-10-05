import os
import gpxpy
import requests
import staticmap
from typing import TypeAlias
from datetime import datetime
from typing import Optional
from geographical import Point, Zone, distance_between_points
from dataclasses import dataclass
from viewer import display_map


@dataclass
class Segment:
    start: Point
    end: Point


Segments: TypeAlias = list[Segment]

MAX_TIME = 100  # maximum time difference acceptable between two points read like xx : xx (min, sec)
MAX_DIST = 0.1  # maximum distance in Km acceptable between two points


def format_date_and_time(
    time: Optional[datetime],
) -> Optional[tuple[int, int]]:  # Optional because time can be None when downloading
    """
    Converts date and time from "datetime" object into a tuple which contains the date and
    time as integers in the format (YYMMDD, HHMMSS)
    """
    if time is not None:
        return (int(time.strftime("%Y%m%d")), int(time.strftime("%H%M%S")))
    return None


def is_segment_valid(
    p1: Point, p2: Point, p1_time: datetime, p2_time: datetime
) -> bool:
    """
    Returns True iff the segment (p1, p2) could realistically happen between times p1_time and p2_time,
    geographically and chronologically speaking (p1 and p2 are not too far apart and the time difference is reasonable)
    """
    time1, time2 = format_date_and_time(p1_time), format_date_and_time(p2_time)
    if time1 and time2:
        if time1[1] > time2[1]:
            return False
        elif (time2[1] - time1[1]) > MAX_TIME:
            return False
        elif time1[0] != time2[0]:
            return False
        elif distance_between_points(p1, p2) > MAX_DIST:
            return False
        return True
    return False


def download_segments(zone: Zone, filename: str) -> None:
    """
    Download all segments in the zone and save them to the file 'filename' in chronological
    order in the following format:  lat1, lon1 - lat2, lon2
    """
    p1, p2 = zone.bottom_left, zone.top_right
    # to insert the zone into the url we need it to be in string format
    zone_string = "{},{}, {},{}".format(p1.lon, p1.lat, p2.lon, p2.lat)

    page = 0
    with open(filename, "w") as file:
        while True:
            try:
                # get the OpenStreetMaps content for the zone
                url = f"https://api.openstreetmap.org/api/0.6/trackpoints?bbox={zone_string}&page={page}"
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                gpx_content = response.content.decode("utf-8")
                gpx = gpxpy.parse(gpx_content)

                if len(gpx.tracks) == 0:
                    break

                for track in gpx.tracks:
                    for segment in track.segments:
                        if all(point.time is not None for point in segment.points):
                            # save two-point segments in chronological order in the file if they are valid
                            segment.points.sort(key=lambda p: p.time)
                            for i in range(len(segment.points) - 1):
                                p1, p2 = segment.points[i], segment.points[i + 1]
                                point1 = Point(float(p1.latitude), float(p1.longitude))
                                point2 = Point(float(p2.latitude), float(p2.longitude))
                                if is_segment_valid(point1, point2, p1.time, p2.time):
                                    file.write(
                                        f"{p1.latitude}, {p1.longitude} - {p2.latitude}, {p2.longitude}\n"
                                    )
                page += 1
            except requests.RequestException as e:
                print(f"An error occurred while fetching data: {e}")
                break  # Exit the loop if there's an error


def load_segments(filename: str) -> Segments:
    """
    Loads segments from the file 'filename' and returns a list of segments.
    Pre: segment data file should have the following format in each line: lat1, lon1 - lat2, lon2
    """
    segments: Segments = []
    with open(filename, "r") as file:
        for line in file:
            # every line is in the format: lat1, lon1 - lat2, lon2
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
    return segments


def get_segments(zone: Zone, filename: str) -> Segments:
    """
    Get all cleaned data of the segments in the box. If filename exists, load segments
    from the file. Otherwise, download segments in the box and save them to the file.
    """
    if not os.path.exists(filename):
        download_segments(zone, filename)
    return load_segments(filename)


def show_segments(segments: Segments, filename: str) -> None:
    """
    Show all segments in a PNG file with name filename using staticmap.
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
    static_map.render().save(filename, format="png")
    # show the map automatically
    display_map(filename)


if __name__ == "__main__":
    pass
