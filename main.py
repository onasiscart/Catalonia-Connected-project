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
    requested_maps: str
    clusters: Optional[int]
    epsilon: Optional[float]
    start_point: Optional[Point]
    files: dict[
        str, str
    ]  # indicators for the filenames: segment_data, segments, graphPNG, graphKML, routesPNG, routesKML, monument_data


def read_zone() -> Zone:
    print("Introduce the geographical coordinates of wour zone separated by spaces: \n")
    p1, p2 = Point(read(float), read(float)), Point(read(float), read(float))
    return Zone(p1, p2)


def read_requested_maps() -> str:
    print(
        f"\nWhat kind of maps do you need? Select a number and press return.\n"
        "   1. Detailed map of the routes in your zone.\n"
        "   2. General map including routes and locations of medieval monuments in your zone.\n"
        "   0. All of them.\n"
    )
    request = read(str)
    while request not in "012":
        print("Not a valid option, try again")
        request = read(str)
    if '1' in request:
        return 'segments'
    elif '2' in request:
        return 'graph'
    elif '0' in request:
        return 'all'


def read_quality() -> tuple[Optional[int], Optional[float]]:
    print(
        f"\nPress 1 to adjust the level of detail you want in your maps.\n"
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
    print("\nIntroduce the coordinates where you will start the route: ", end="")
    return Point(read(float), read(float))


def read_filenames(requested_maps: str) -> dict[str, str]:
    """
    reads all the filenames needed for the execution and returns a dictionary with key words
    (specified in the input dataclass) and their names.
    """
    files: dict[str, str] = {}
    print(
        f"\nIntroduce the names you want to give to the following files that will be generated. If you already\n"
        "have the data collected in a file.txt, also name it (without the extension). If not, be sure to have\n"
        "internet connection during the download.\n"
    )

    print(f"\nSegments data file: ", end="")
    files['segment_data'] = read(str) + ".txt"

    if requested_maps == 'segments' or requested_maps == 'all':
        print(f"\nDetailed map: ", end="")
        files["segments"] = read(str) + ".png"

    if requested_maps == "graph" or requested_maps == "all":
        print(f"\nMonuments data file: ", end="")
        files['monument_data'] = read(str) + '.txt'

        print(f"\nGeneral 2D map: ", end="")
        files["graphPNG"] = read(str) + ".png"

        print(f"\n2D map of the routes: ", end="")
        files["routesPNG"] = read(str) + ".png"

        print(f"\nGeneral 3D map: ", end="")
        files["graphKML"] = read(str) + ".kml"

        print(f"\n3D map of the routes: ", end="")
        files["routesKML"] = read(str) + ".kml"

    return files


def read_parameters() -> Input:
    """
    reads and returns all the input settings
    """
    map_zone = read_zone()
    requested_maps = read_requested_maps()

    if requested_maps == "all" or requested_maps == "graph":
        clusters, epsilon = read_quality()
        start_point = read_start_point()
    else:
        clusters = epsilon = start_point = None

    return Input(map_zone, requested_maps, clusters, epsilon, start_point, read_filenames(requested_maps))


def print_welcome_message() -> None:
    print(
        f"\nWELCOME TO (NOM DE LA APLIACICÓ)! This app will let you generate route maps of any zone in our beautiful Catalonia.\n"
        "The maps will show lots detailed paths in your zone, as well as different medieval monuments you can visit and the\n"
        "shortest ways to reach them. Enjoy your walk!\n"
    )


def open_google_earth(url):
    """
    Opens the URL 'url' in the default web browser.
    """
    try:
        webbrowser.open(url)
        print(f"Successfully opened {url}")
    except Exception as e:
        print(f"An error occurred while trying to open Google Earth: {e}")


def main() -> None:
    print_welcome_message()
    settings = read_parameters()
    print(f"\nGenarating your maps. This might take a while...")

    if settings.requested_maps == "all" or settings.requested_maps == "segments":
        show_segments(
            get_segments(settings.map_zone, settings.files["segment_data"]),
            settings.files["segments"],
        )

    if settings.requested_maps == "all" or settings.requested_maps == "graph":
        graph = get_graph(get_segments(settings.map_zone, settings.files['segment_data']), settings.clusters, settings.epsilon)
        monuments: Monuments = get_monuments(settings.map_zone, settings.files['monument_data'])
        routes = find_routes(graph, settings.start_point, monuments)

        export_graph_PNG(graph, settings.files['graphPNG'])
        export_routes_PNG(routes, settings.files['routesPNG'])

        export_graph_KML(graph, settings.files['graphKML'])
        export_routes_KML(routes, settings.files['routesKML'])

    #print_end_message()
    #open_google_earth('https://www.google.es/intl/es/earth/index.html')



if __name__ == "__main__":
    main()


#          0.5739316671 40.5363713 0.9021482 40.79886535             ebre

#          40.5363713 0.5739316671 40.79886535 0.9021482            ebre

#          40.692481   0.651148           ruta

#                     ruta


# 41.523897 2.074469  41.807045 2.513922  valles oriental

#   41.548676 2.246927 casa meva

# 41.542625  2.263915 casa abril


# 41.597703   1.949020   41.681057  2.168082   Matadepera

#  41.630280  2.007482   casa Ona



# 42.258556 3.144315  42.345739 3.310615 cap de creus

#  42.289634  3.210129

# 0.699934 42.653002  1.021971 42.782149 vall d'aran

#

#graph_not_simp = get_not_simplified(get_segments(settings.map_zone, settings.files['data']), settings.clusters, settings.epsilon)
