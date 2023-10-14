import re
from typing import TypedDict, List
import requests
from bs4 import BeautifulSoup, ResultSet
import csv

DOMAIN = 'https://www.invader-spotter.art/'
URL = DOMAIN + 'listing.php'
#IMG_BASE_URL = 'https://www.invader-spotter.art/%s'
#EXCEL_FORMULA = '=IMAGE("%s")' % IMG_BASE_URL

INVADER_ID_POINTS_PATTERN = r'<b>([A-Z]+_[0-9]+) \[([?0-9]{2,3} pts)\]<\/b>'
#INVADER_LOCATION_PATTERN = r'<br\/>\((.*)\)<br>'
INVADER_STATUS_DESCRIPTION_PATTERN = r'Dernier état connu : <img.*> (.*)<br.?>'
#INVADER_DATE_PATTERN = r'Date et source : (.*)<.?br>'


data={'numero':'',
'choixmotif':'ou',
'choixfond':'ou',
'couleurmotif':'0000000000000000000',
'couleurfond':'0000000000000000000',
'x':99,
'y':14,
'page':1,
'arron':'00'}


class Invader(TypedDict):
#    icon_url: str
    name: str
    points: str
#   status: str
    status_description: str
#   location: str
#   date: str
    picture_url: str



invaders: List[Invader] = []
while True:
    response = requests.post(URL, data, headers={'Referer': 'https://www.invader-spotter.art/villes.php'})
    soup = BeautifulSoup(response.text, "html.parser")
    invaders_rows: ResultSet = soup.find_all('tr', {'class': 'haut'})

    if len(invaders_rows) == 0:
        break
    else:
        data['page'] += 1

    for row in invaders_rows:
   #     icon_url = row.find('td', {'align': 'left'}).find('img')['src']
   #     status_image_url = row.find('td', {'align': 'left'}).find('font').find('img')['src']

        picture_url_html_tag = row.find('a', {'class': 'chocolat-image'})
        picture_url = picture_url_html_tag['href'] if picture_url_html_tag else None

        description = str(row.find('td', {'align': 'left'}).find('font'))

        match = re.search(INVADER_ID_POINTS_PATTERN, description)
        name = match.group(1) if match else None
        points = match.group(2) if match else None
        points=re.split(" ",points)[0] if points else None

        match = re.search(INVADER_STATUS_DESCRIPTION_PATTERN, description)
        status_description = match.group(1) if match else None
        status_description = re.split("<",status_description)[0]

        #match = re.search(INVADER_LOCATION_PATTERN, description)
        #location = match.group(1) if match else None

        #match = re.search(INVADER_DATE_PATTERN, description)
        #date = match.group(1) if match else None

        invader = Invader(name=name, 
                          points=points,
                          status_description=status_description,
                          picture_url=DOMAIN+picture_url if picture_url else None
                          )
        invaders.append(invader)

    with open('invaders-updated.csv' , 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=invaders[0].keys())
        writer.writeheader()
        writer.writerows(invaders)
