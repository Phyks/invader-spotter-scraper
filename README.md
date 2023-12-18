invader-spotter-scraper
=======================

Space Invaders Spotter - Street Art website scraper


## Installation

```
python -m venv .venv
./.venv/bin/pip install -r requirements.txt
```


## Usage

### Scraping known Invaders and locations

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

### Generating a KML of all remaining invaders

Provided you have a KML file of your flashed invaders (or a GPX and convert it
to KML), you can run

```
./.venv/bin/python generate_to_flash.py KML_FILE_OF_FLASHED_INVADERS
```

to generate a `data/invaders-to-flash.kml` KML file containing all the known
invaders locations that you did not flash and that are known to be active at
the moment.


## License

Forked and adapted from https://github.com/Zboubinours/invader-spotter-scraper
which did not specify an initial license. For extra code on top of this
original one, it can be considered public domain.
