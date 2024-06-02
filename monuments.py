from dataclasses import dataclass
from typing import TypeAlias
import requests
from bs4 import BeautifulSoup, Tag
import os
import re
from geographical import *


@dataclass
class Monument:
    name: str
    location: Point


Monuments: TypeAlias = list[Monument]


def download_monuments(filename: str) -> None:
    """
    Download monuments to a file named "filename" from Catalunya Medieval.
    Every line in the file will have the following format: monument name: latitude, longitude
    """
    with open(filename, "w") as file:
        monuments = find_monuments()
        if monuments:
            # transform JSON script to text and search for names and coordinates of each monument
            text = monuments.text
            # this will look for patterns like:  "title":"Ajuntament d\u2019Arnes ", "title":"Ca l\u2019Amar de la Torre"
            name_pattern = r'"title":"(.*?)"'
            # this will look for patterns like:  position":{"lat":"40.953871","long":"0.316882"}
            coords_pattern = r'"position":{"lat":"(.*?)","long":"(.*?)"}'
            # use the patterns to find the names and coordinates of all monuments
            names = re.findall(name_pattern, text)
            coord_strings = re.findall(coords_pattern, text)
            for name, coord in zip(names, coord_strings):
                # the following will turn things like "Ajuntament d\u2019Arnes" to "Ajuntament d�Arnes",
                # which will allow us to write "Ajuntament d'Arnes" to the output
                monument_name = bytes(name, "utf-8").decode("unicode_escape")
                file.write(f"{monument_name}:{float(coord[0])},{float(coord[1])}\n")
    file.close()


def find_monuments() -> Tag | None:
    """
    Finds and returns an html tag with a script containing all the monument information that we need from CatalunyaMedieval
    """
    url = "https://www.catalunyamedieval.es/comarques/"
    # search for url, it's usually slow so we indicate that with a timeout
    response = requests.get(url, timeout=60)
    soup = BeautifulSoup(response.text, "html.parser")
    # we look for a javascript script with the information on all the monuments
    scripts = soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        # the script contains the following line towards the start
        if "var aCasaForta" in str(script):
            return script


def load_monuments(box: Zone, filename: str) -> Monuments:
    """
    Load information of monuments in the geographical box from the file "filename".
    Pre: every line in the file follows the format: monument name: latitude, longitude
    """
    file = open(filename, "r")
    monuments: list[Monument] = []
    for line in file:
        # every line in the file is "name: latitude, longitude"
        name, coord_str = line.split(":")
        lat, lon = coord_str.split(",")
        coord = Point(float(lat), float(lon))  # lat and lon were strings
        if in_zone(box, coord):
            monuments.append(Monument(name, coord))
    file.close()
    return monuments


def get_monuments(box: Zone, filename: str) -> Monuments:
    """
    Get all monuments in the box.
    If filename exists, load monuments from the file.
    Otherwise, download monuments and save them to the file, then load them.
    """
    if not os.path.exists(filename):
        download_monuments(filename)
    return load_monuments(box, filename)


if __name__ == "__main__":
    pass
