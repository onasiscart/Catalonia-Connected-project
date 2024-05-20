
from graphmaker import *
from segments import *
from viewer import *
from geographical import *


def main() -> None:
    BOX_EBRE = Zone(Point(0.5739316671, 40.5363713), Point(0.9021482, 40.79886535))
    segments = get_segments(BOX_EBRE, "data_EBRE.txt")
    view_clusters(segments, 100)
    G = make_graph(segments, 100)
    export_PNG(G, "prova2.png")


if __name__ == "__main__":
    main()
