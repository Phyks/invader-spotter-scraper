#!/usr/bin/env python
import argparse
import csv
import re
import sys

import fastkml
import gpxpy

from kml import generate_kml


class MockFeature():
    """
    Mock Feature object to handle GPX the same way as KML files.
    """
    def __init__(self, name):
        self.name = name


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='append', help='GPX or KML file(s) of flashed invaders.', required=True)
    parser.add_argument('-e', '--exclude', help='A GPX file of known buggy invaders.')
    args = parser.parse_args()

    # Load user-provided KML file
    features = []
    for inputfile in args.input:
        if inputfile.endswith('.kml'):
            k = fastkml.kml.KML()
            with open(inputfile, 'rb') as fh:
                k.from_string(fh.read())

            kml_features += list(k.features())
            # Iterate over Document, Folder etc. to find features
            # TODO: Only support nested structure with a single Folder
            while True:
                try:
                    kml_features = list(kml_features[0].features())
                except AttributeError:
                    break
            features.extend(kml_features)
        elif inputfile.endswith('.gpx'):
            with open(inputfile, 'r') as fh:
                gpx = gpxpy.parse(fh)
            for point in gpx.waypoints:
                features.append(MockFeature(point.name))
        else:
            sys.exit(f'Unsupported input file: {inputfile}.')

    excluded = []
    with open(args.exclude, 'r') as fh:
        gpx = gpxpy.parse(fh)
        excluded = [point.name for point in gpx.waypoints]

    # Load all the known invaders with locations
    with open('data/invaders-with-locations.csv', 'r') as fh:
        reader = csv.DictReader(fh)
        invaders = list(reader)
    invaders_by_name = {
        invader['name']: invader
        for invader in invaders
    }

    # Match flashed invaders (from the KML) with known invaders
    matched_invaders = []
    for feature in features:
        feature_name = feature.name.upper().replace('-', '_')
        name = re.search('[A-Z]+_[0-9]+', feature_name)
        if not name:
            print('Ignored:', feature_name)
            continue
        name = name.group(0)

        invader_match = None
        while not invader_match:
            try:
                invader_match = invaders_by_name[name]
            except KeyError:
                if '_0' not in name:
                    print('Not found:', name)
                    break
                name = name.replace('_0', '_')
        matched_invaders.append(name)

    # Output a filtered KML file with only the remaining invaders (working and
    # not flashed)

    # Filter out already flashed invaders
    invaders_to_flash = [
        invader
        for invader in invaders
        if invader['name'] not in matched_invaders
    ]
    # Filter out unflashable invaders
    working_invaders_to_flash = [
        invader
        for invader in invaders_to_flash
        if invader['status_description'] not in ['Détruit !', 'Non visible']
    ]
    # Filter out buggy invaders
    nonbuggy_working_invaders_to_flash = [
        invader
        for invader in working_invaders_to_flash
        if invader['name'] not in excluded
    ]

    generate_kml(
        invaders=nonbuggy_working_invaders_to_flash,
        out_file='data/invaders-to-flash.kml',
        name='Invaders left to flash',
    )
    print('%s invaders left to flash!' % len(nonbuggy_working_invaders_to_flash))
