#!/usr/bin/env python
"""
Scrape invaders from invader-spotter.art and add locations from various
sources.
"""
import collections
import csv
import re
from typing import TypedDict, List

import fastkml
import requests
from bs4 import BeautifulSoup, ResultSet
from prettytable import PrettyTable, MARKDOWN
from pygeoif.geometry import Point

DOMAIN = 'https://www.invader-spotter.art/'
URL = DOMAIN + 'listing.php'

INVADER_ID_POINTS_PATTERN = r'<b>([A-Z]+_[0-9]+) \[([?0-9]{2,3} pts)\]<\/b>'
INVADER_STATUS_DESCRIPTION_PATTERN = r'Dernier état connu : <img.*> (.*)<br.?>'

# Order is important there, the first source for a given Invader is the ground
# truth.
SOURCE_GEOJSON = [
    # https://umap.openstreetmap.fr/fr/map/dump-positions-des-invaders-18122024_1000818
    'https://umap.openstreetmap.fr/fr/datalayer/1000818/3083389/',
    # https://umap.openstreetmap.fr/fr/map/space-invaders_425001
    'https://umap.openstreetmap.fr/fr/datalayer/425001/1180599/',
    # https://umap.openstreetmap.fr/fr/map/invader-world_952127
    'https://umap.openstreetmap.fr/fr/datalayer/952127/2923771/',
]


class Invader(TypedDict):
    name: str
    points: str
    status_description: str
    picture_url: str


def scrape(url=URL, out_file='data/invaders-dump.csv'):
    """
    Scrape all invaders pages from invader-spotter.art.

    Writes output to out_file CSV file.
    """
    invaders: List[Invader] = []
    data = {
        'numero': '',
        'choixmotif': 'ou',
        'choixfond': 'ou',
        'couleurmotif': '0000000000000000000',
        'couleurfond': '0000000000000000000',
        'x': 99,
        'y': 14,
        'page': 1,
        'arron': '00'
    }
    while True:
        response = requests.post(
            url,
            data,
            headers={'Referer': DOMAIN + 'villes.php'}
        )
        soup = BeautifulSoup(response.text, "html.parser")
        invaders_rows: ResultSet = soup.find_all('tr', {'class': 'haut'})

        if not invaders_rows:
            break

        data['page'] += 1
        for row in invaders_rows:
            picture_url_html_tag = row.find('a', {'class': 'chocolat-image'})
            picture_url = (
                picture_url_html_tag['href'] if picture_url_html_tag else None
            )

            description = str(row.find('td', {'align': 'left'}).find('font'))

            match = re.search(INVADER_ID_POINTS_PATTERN, description)
            name = match.group(1) if match else None
            points = match.group(2) if match else None
            points = re.split(" ", points)[0] if points else None

            match = re.search(INVADER_STATUS_DESCRIPTION_PATTERN, description)
            status_description = match.group(1) if match else None
            status_description = re.split("<", status_description)[0]

            invader = Invader(
                name=name,
                points=points,
                status_description=status_description,
                picture_url=DOMAIN+picture_url if picture_url else None
            )
            invaders.append(invader)

        with open(out_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=invaders[0].keys())
            writer.writeheader()
            writer.writerows(invaders)


def add_locations(
    in_file='data/invaders-dump.csv',
    out_file='data/invaders-with-locations.csv',
    source_geojson=SOURCE_GEOJSON
):
    """
    Reads from the output of scrape function (CSV file in_file) and fuse with
    GeoJSON sources for Invaders locations. Writes the output to the CSV file
    out_file.
    """
    with open(in_file, 'r') as fh:
        reader = csv.DictReader(fh)
        invaders = list(reader)

    invaders_locations = {}
    for geojson in source_geojson:
        result = requests.get(geojson).json()
        for feature in result['features']:
            name = re.search(
                r'[A-Z]+_[0-9]+',
                feature['properties'].get('name', '')
            )
            if not name:
                continue
            name = name.group(0)
            if name in invaders_locations:
                # Already handled
                continue
            description = feature['properties']['name']
            coordinates = feature['geometry']['coordinates']
            invaders_locations[name] = {
                'description': description,
                'coordinates': coordinates
            }

    for invader in invaders:
        name = invader['name']
        invader['description'] = None
        invader['lon'], invader['lat'] = None, None

        for _ in range(3):
            if name not in invaders_locations:
                name = name.replace('_', '_0')
                continue
            location = invaders_locations[name]
            invader['description'] = location['description']
            invader['lon'], invader['lat'] = location['coordinates']

    with open(out_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=invaders[0].keys())
        writer.writeheader()
        writer.writerows(invaders)


def _compute_color(invader):
    """
    Compute KML color based on invader points and status.
    """
    if invader['status_description'] == 'OK':
        if int(invader['points']) == 100:
            return 'pink'
        elif int(invader['points']) == 50:
            return 'purple'
    elif invader['status_description'].startswith('Détruit'):
        return 'red'
    elif invader['status_description'] == 'Dégradé':
        return 'brown'
    return 'yellow'


def generate_kml(
    in_file='data/invaders-with-locations.csv',
    out_file='data/all-invaders.kml'
):
    """
    Generate a GPX file from all known invaders with their locations.
    """
    kml = fastkml.kml.KML()

    ns = '{http://www.opengis.net/kml/2.2}'
    d = fastkml.kml.Document(
        ns,
        name='All invaders',
        styles=[
            fastkml.styles.Style(
                ns,
                'placemark-%s' % color,
                styles=[
                    fastkml.styles.IconStyle(
                        ns,
                        icon_href=(
                            'https://omaps.app/placemarks/placemark-%s.png' %
                            color
                        )
                    )
                ]
            )
            for color in ['pink', 'purple', 'red', 'brown', 'yellow']
        ]
    )
    kml.append(d)

    missing_coordinates_by_status = collections.defaultdict(list)

    with open(in_file, 'r') as fh:
        reader = csv.DictReader(fh)
        invaders = list(reader)

    for invader in invaders:
        if not invader['lat'] and not invader['lon']:
            # No GPS coordinates
            status = invader['status_description']
            missing_coordinates_by_status[status].append(
                invader['name']
            )
            continue
        name = invader['name']
        description = (
            'status=%s ; points=%s ; image="%s" ; desc="%s"' %
            (invader['status_description'], invader['points'],
             invader['picture_url'], invader['description'])
        )
        p = fastkml.kml.Placemark(
            ns, name=name, description=description,
            styleUrl=('#placemark-%s' % _compute_color(invader))
        )
        p.geometry = Point(invader['lon'], invader['lat'])
        d.append(p)

    with open(out_file, 'w') as fh:
        fh.write(kml.to_string(prettyprint=True))

    # Debug
    table = PrettyTable()
    table.field_names = ["Status", "# of missing locations"]
    table.align["Status"] = "l"
    table.set_style(MARKDOWN)
    for status, items in missing_coordinates_by_status.items():
        table.add_row([status, len(items)])
    print(table.get_string(sortby="# of missing locations", reversesort=True))


if __name__ == '__main__':
    # scrape()
    add_locations()
    generate_kml()
