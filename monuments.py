from dataclasses import dataclass
from typing import TypeAlias
import requests
from bs4 import BeautifulSoup, Tag
import os
import re
from geographical import *

# TODO:
# error handling
# monument_classes = ["castell", "epoca-carlina", "muralles", "torre", "casa-forta", ""]


@dataclass
class Monument:
    name: str
    location: Point


Monuments: TypeAlias = list[Monument]


def download_monuments(filename: str) -> None:
    """
    Download monuments from Catalunya Medieval.
    """
    with open(filename, "w") as file:
        monuments = find_monuments()
        if monuments:
            # transformarem el script de JSON a text i buscarem els noms i coordenades de cada monument
            text = monuments.text
            # el següent serveix per buscar coses com: ...
            name_pattern = r'"title":"(.*?)"'
            #
            coords_pattern = r'"position":{"lat":"(.*?)","long":"(.*?)"}'
            # trobem els noms dels monuments i les seves coordenades
            names = re.findall(name_pattern, text)
            coord_strings = re.findall(coords_pattern, text)
            # escrivim els noms i coordenades dels monuments al fitxer
            for name, coord in zip(names, coord_strings):
                # el següent ...
                monument_name = bytes(name, "utf-8").decode("unicode_escape")
                file.write(f"{monument_name}:{float(coord[0])},{float(coord[1])}\n")
    file.close()


def find_monuments() -> Tag | None:
    """..."""
    url = "https://www.catalunyamedieval.es/comarques/"
    # busquem l'url, sol ser lent per tant avisem amb timeout
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")
    # busquem un script de javascript on hi ha tota la informació dels monuments que necessitem
    scripts = soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        # el script comença amb el string següent
        if "var aCasaForta" in str(script):
            return script


def load_monuments(box: Zone, filename: str) -> Monuments:
    """Load monuments from a file."""
    with open(filename, "r") as file:
        monuments: list[Monument] = []
        for line in file:
            # cada línia del fitxer serà "nom, latitud, longitud"
            name, coord_str = line.split(":")
            lat, lon = coord_str.split(",")
            coord = Point(float(lat), float(lon))  # lat i lon eren strings
            if in_zone(box, coord):
                monuments.append(Monument(name, coord))
    return monuments


def in_zone(box: Zone, coord: Point) -> bool:
    """returns True iff coord is inside the box"""
    # assumim que la zona es proub petita per no haver de tenir en compte la curvatura de la terra
    return (
        box.bottom_left.lat <= coord.lat <= box.top_right.lat
        and box.bottom_left.lon <= coord.lon <= box.top_right.lon
    )


def get_monuments(box: Zone, filename: str) -> Monuments:
    """
    Get all monuments in the box.
    If filename exists, load monuments from the file.
    Otherwise, download monuments and save them to the file.
    """
    if not os.path.exists(filename):
        download_monuments(filename)
    return load_monuments(box, filename)


def main() -> None:
    BOX_EBRE = Zone(Point(0.5739316671, 40.5363713), Point(0.9021482, 40.79886535))
    get_monuments(BOX_EBRE, "monuments1.dat")


if __name__ == "__main__":
    main()
