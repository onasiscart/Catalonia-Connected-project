from segments import *
from geographical import *
from viewer import *
from yogi import *
from graphmaker import *
from dataclasses import dataclass
import webbrowser
from routes import *
from monuments import *


@dataclass
class Input:
    map_zone: Zone

    requested_maps: str  # this will either be "graph", "segments", "routes" or "all"
    clusters: Optional[int]
    epsilon: Optional[float]
    start_point: Optional[Point]
    files: dict[
        str, str
    ]  # keys: segment_data, segments, graphPNG, graphKML, routesPNG, routesKML, monument_data


def generate_requested_maps(settings: Input) -> None:
    """
    Generates and shows the requested maps according to the settings input by the user
    """
    # we will need to get the segments no matter what map we want to show:
    segments = get_segments(settings.map_zone, settings.files["segment_data"])
    assert segments != []

    if settings.requested_maps in ("all", "segments"):
        # we need to show the segments
        show_segments(
            segments,
            settings.files["segments"],
        )

    if settings.requested_maps != "segments":
        # we either needd to generate routes, all or graph maps
        # we need a graph in any case
        graph = get_graph(
            segments,
            settings.clusters,
            settings.epsilon,
        )
        # do we need to show the graph?
        if settings.requested_maps in ("graph", "all"):
            export_graph_PNG(graph, settings.files["graphPNG"])
            export_graph_KML(graph, settings.files["graphKML"])
        # do we need to generate and show routes?
        if settings.requested_maps in ("routes", "all"):
            monuments: Monuments = get_monuments(
                settings.map_zone, settings.files["monument_data"]
            )
            routes = find_routes(graph, settings.start_point, monuments)
            export_routes_PNG(routes, settings.files["routesPNG"])
            export_routes_KML(routes, settings.files["routesKML"])


def read_zone() -> Zone:
    """
    reads and returns a zone
    """
    print("Latitude of the lower left corner of your area:")
    bl_lat = read(float)
    print("\nLongitude of the lower left corner of your area:")
    bl_lon = read(float)
    print("\nLatitude of the upper rigt corner of your area:")
    tr_lat = read(float)
    print("\nLatitude of the lower left corner of your area:")
    tr_lon = read(float)
    return Zone(Point(bl_lat, bl_lon), Point(tr_lat, tr_lon))


def read_requested_maps() -> str:
    """
    Presents different options of maps the user can choose to generate and returns a string indicating the option chosen
    """
    # present options
    print(
        f"\nWhat kind of maps do you need? Select a number and press return.\n"
        "   0. Detailed map of OpenStreetMaps routes in your area.\n"
        "   1. A simplified graph of all routes and paths in your area\n"
        "   2. A graph showing the shortest routes from a certain location to the medieval monuments in your area\n"
        "   3. All of them.\n"
    )
    # read the number chosen
    request = read(str)
    # error handling
    while request not in "0123":
        print("Please enter a number corresponding to one of the available options.")
        request = read(str)
    # match the number entered to an option
    if "0" in request:
        return "segments"
    elif "1" in request:
        return "graph"
    elif "2" in request:
        return "routes"
    assert "3" in request
    return "all"


def read_quality() -> tuple[Optional[int], Optional[float]]:
    """
    Presents the user with the option to adjust the number of clusters and angle to simplify edges for the creation of the graph.
    Reads and returns the tuple (#clusters, epsilon) if the user chooses to adjust them, otherwise (None,None).
    """
    # present option to adjust parameters
    print(
        f"\nWe will be making a graph to generate your maps."
        f"\nPress 1 to adjust the level of detail you want in your graph.\n"
        "Press 0 and the quality will be set with default values.\n"
    )
    quality = read(str)
    while quality not in "01":
        print("Not a valid option, select 0 or 1.\n")
        quality = read(str)

    if quality == "1":
        print(f"\nSelect the number of clusters: ", end="")
        n_clusters = read(int)
        print(f"\nSelect the minimum angle between segments in the graph: ", end="")
        epsilon = read(float)
        return (n_clusters, epsilon)
    else:
        return (None, None)


def read_start_point() -> Point:
    """
    Reads and returns the starting point Point(latitude, longitude) of a route.
    """
    print("\nWhere do you want to start the route? Enter coordinates below", end="")
    print("\n Latitude of your starting point: ", end="")
    lat = read(float)
    print("\nLongitude of your starting point: ", end="")
    lon = read(float)
    return Point(lat, lon)


def read_filenames(requested_maps: str) -> dict[str, str]:
    """
    Reads all the filenames needed for the execution and returns a dictionary with keys
    [segment_data, segments, graphPNG, graphKML, routesPNG, routesKML, monument_data]
    and the names read as the corresponding values.
    """
    files: dict[str, str] = {}
    print(
        f"\nWe will now ask you what you want to name the files we will generate for you. Please introduce filenames without their extension."
        f"\nPlease note:"
        f"\n-If you already have .txt files with the data you want to use to generate your maps, enter their names as well."
        f"\n-Once you have a monument data file you can reuse it for any zone. This is NOT the same for segments!"
        f"\n-Be sure not to name the segment files for two different areas the same!"
        f"\n-For maps containing the graph and monument routes, two files will be generated: a 2D .png file and a 3D .kml file, both with the same name"
    )

    # we will always need segment data
    print(f"\nFile with segment data from OpenStreetMaps: ", end="")
    files["segment_data"] = read(str) + ".txt"

    # we will need different files for different map options
    if requested_maps in ("graph", "all"):
        # we will need to generate maps containing the graph
        print(f"\nSimplified graph of all paths and routes in your area: ", end="")
        filename = read(str)
        files["graphPNG"], files["graphKML"] = filename + ".png", filename + ".kml"

    if requested_maps in ("routes", "all"):
        # we will need to read from a file with monument data
        print(f"\nFile containing monument data: ", end="")
        files["monument_data"] = read(str) + ".txt"
        # we will need to generate maps with shortest routes to the monuments
        print(f"\nMap with the shortest routes to monuments around you: ", end="")
        filename = read(str)
        files["routesPNG"], files["routesKML"] = filename + ".png", filename + ".kml"

    if requested_maps in ("segments", "all"):
        print(f"\nDetailed map of OpenStreetMaps routes: ", end="")
        files["segments"] = read(str) + ".png"
    return files


def read_input() -> Input:
    """
    Reads and returns all the input settings
    """
    map_zone = read_zone()
    requested_maps = read_requested_maps()
    # we read extra parameters depending on the requested maps
    if requested_maps != "segments":
        # We have requested either graph, routes or all maps
        # we need extra input
        clusters, epsilon = read_quality()
        start_point = None if requested_maps == "graph" else read_start_point()
    else:
        # we do not need any extra input
        clusters = epsilon = start_point = None

    return Input(
        map_zone,
        requested_maps,
        clusters,
        epsilon,
        start_point,
        read_filenames(requested_maps),
    )


def print_welcome_message() -> None:
    """
    Prints a message to welcome the user to the app
    """
    print(
        f"\nWELCOME TO CATALONIA CONNECTED! This app will let you generate route maps of any zone in our beautiful Catalonia.\n"
        "The maps will show lots detailed paths in your zone, as well as different medieval monuments you can visit and the\n"
        "shortest ways to reach them. Enjoy your walk!\n"
    )


def main() -> None:
    print_welcome_message()
    settings = read_input()
    print(f"\nGenarating your maps. This might take a while...")
    generate_requested_maps(settings)
 


if __name__ == "__main__":
    main()
