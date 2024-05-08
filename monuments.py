from dataclasses import dataclass
from typing import TypeAlias
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from locations import Zone
import os
import re

# TODO:
# -decidir si canviar la llista "pages" a un scrape dels menu-items de la soup
# -error handling -> si response.status_code és diferent a 200 OK tenim un problema. Podem fer if response i ja ens diu si hi ha hagut success o no
#
# - volem localització del monument amb el nom o no? Sí
#petit va dir que era millor descarregar tots els monuments


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Monument:
    name: str
    location: Point


Monuments: TypeAlias = list[Monument]

classes_monuments = ...


def download_monuments(filename: str) -> None:
    """
    Download monuments from Catalunya Medieval.
    """
    with open(filename, "w") as file:
        monuments = find_monuments(comarca)
        for monument in monuments:
            name = get_monument_name(monument)
            lat, lon = get_monument_coords(monument)
            file.write(f"{name}-{lat}-{lon}\n")


def comarques_in(zone: Zone) -> list[str]: ...


def find_monuments(comarca: str) -> ResultSet[Tag]:
    """..."""
    url = f"https://www.catalunyamedieval.es/{comarca}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    monuments = soup.find_all("li", class_=...)
    print(monuments)
    return monuments


def get_monument_name(monument: Tag) -> str:
    """busca i retorna el nom del monument"""
    link = monument.find("a")
    assert link  # sinó haurem de fer error handling!
    name = link.text.split("-")[0]
    # el format del text sempre és "num. nom del monument - localització"
    print(name)
    return name


def get_monument_coords(monument: Tag) -> tuple[float, float]:
    # aquesta funció no m'agrada gens però gens
    """"""
    link = monument.find("a")
    assert isinstance(link, Tag)  # else ves a saber
    url = link.get("href")
    assert type(url) == str
    monument_reponse = requests.get(url)
    soup = BeautifulSoup(monument_reponse.text, "html.parser")
    a_tags = soup.find_all("a", href=re.compile(r"goo\.gl/maps"))
    # aquesta cosa que ve ara no l'entenc
    coordinates_a_tag = next(
        tag
        for tag in a_tags
        if re.match(r"N \d+ \d+ \d+\.\d+ E \d+ \d+ \d+\.\d+", tag.text)
    )
    assert coordinates_a_tag
    # Extract the text content of the <a> tag
    coord_text = coordinates_a_tag.text
    coord_values = re.findall(r"\d+\.\d+|\d+", coord_text)
    latitude = float("".join(coord_values[:3]))
    longitude = float("".join(coord_values[3:]))
    return latitude, longitude


def load_monuments(filename: str) -> Monuments:
    """Load monuments from a file."""
    # dependrà del format del fitxer, de moment ho faig amb pickle que ens permetria guardar qualsevol cosa
    file = open(filename, "r")  # potser rb si fem servir pickle al final
    return [Monument("name", Point(0.2, 0.4))]


def get_monuments(box: Zone, filename: str) -> Monuments:
    """
    Get all monuments in the box.
    If filename exists, load monuments from the file.
    Otherwise, download monuments and save them to the file.
    """
    if not file_exists(filename):
        download_monuments(box, filename)
    return load_monuments(filename)


def file_exists(filename: str) -> bool:
    """
    Returns True iff the filename exists in the current working directory
    """
    return os.path.exists(filename)
    # filename serà ja am çb el .dat o no????


def main() -> None:
    url = "https://www.catalunyamedieval.es/castell-dalio-alt-camp/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")


main()
