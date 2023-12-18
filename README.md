invader-spotter-scraper
=======================

Space Invaders Spotter - Street Art website scraper


## Installation

```
python -m venv .venv
./.venv/bin/pip install -r requirements.txt
```


## Usage

First, scrape all known invaders together with their status and location:

```
./.venv/bin/python scraper.py
```

This will generate 3 files:
* `data/invaders-dump.csv`, a CSV dump of all the invaders from
    invader-spotter.art.
* `data/invaders-with-locations.csv`, the CSV with the additional locations
    information.
* `data/all-invaders.kml`, a ready to import KML file with all the invaders as
    bookmarks/placemarks.


## License

Forked and adapted from https://github.com/Zboubinours/invader-spotter-scraper
which did not specify an initial license. For extra code on top of this
original one, it can be considered public domain.
