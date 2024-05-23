from segments import *
from geographical import *
from viewer import *
from yogi import *
from graphmaker import *
from dataclasses import dataclass
import webbrowser


@dataclass
class Input:
    map_zone: Zone
    requested_maps: str
    clusters: Optional[int]
    epsilon: Optional[float]
    start_point: Optional[float]
    files: dict[
        str, str
    ]  # indicators for the filenames: data, segments, graphPNG, graphKML, routesPNG, routesKML


def read_zone() -> Zone:
    print("Introduce the geographical coordinates of wour zone separated by spaces: \n")
    # make zone ????
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
    if "1" in request:
        return "segments"
    elif "2" in request:
        return "graph"
    elif "0" in request:
        return "all"


def read_quality() -> tuple[int, float]:
    print(
        f"\nPress 1 to select the level of detail you request in your maps.\n"
        "Press 0 and the quality will be automatically generated.\n"
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
    
    else: 
        n_clusters = epsilon = None

    return (n_clusters, epsilon)


def read_start_point() -> Point:
    print("\nIntroduce the coordinates where you request to start the route: ", end="")
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

    print(f"\nData file: ", end="")
    files["data"] = read(str) + ".txt"

    if requested_maps == "segments" or requested_maps == "all":
        print(f"\nDetailed map: ", end="")
        files["segments"] = read(str) + ".png"

    if requested_maps == "graph" or requested_maps == "all":
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

    files = read_filenames(requested_maps)

    return Input(map_zone, requested_maps, clusters, epsilon, start_point, files)


def print_welcome_message() -> None:
    print(
        f"\nWELCOME TO (NOM DE LA APLIACICÓ)! This app will let you generate route maps of any zone in our beautiful Catalonia.\n"
        "The maps will show lots detailed paths in your zone, as well as different medieval monuments you can visit and the\n"
        "shortest ways to reach them. Enjoy your walk!\n"
    )


def open_google_earth(url):
    """
    Open a URL in the default web browser.

    Parameters:
    url (str): The URL to be opened.
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
            get_segments(settings.map_zone, settings.files["data"]),
            settings.files["segments"],
        )

    if settings.requested_maps == "all" or settings.requested_maps == "graph":
        graph = get_graph(get_segments(settings.map_zone, settings.files['data']), settings.clusters, settings.epsilon)
        #graph = get_graph_2(get_segments(settings.map_zone, settings.files['data']), settings.clusters, settings.epsilon)

        export_PNG(graph, settings.files['graphPNG'])
        # routes.export_PNG(routes, settings.files['routesPNG'])

        export_KML(graph, settings.files['graphKML'])
        # routes.export_KML(routes, settings.files['routesKML'])

    # print_end_message()
    open_google_earth('https://www.google.es/intl/es/earth/index.html')



if __name__ == "__main__":
    main()


# 0.5739316671 40.5363713 0.9021482 40.79886535 ebre

# 2.074469 41.523897 2.513922 41.807045 valles oriental

# 3.144315 42.258556  3.310615 42.345739 cap de creus

# 0.699934 42.653002  1.021971 42.782149 vall d'aran
