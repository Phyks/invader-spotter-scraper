#!/uhttpssr/bin/env python
import csv
import re
import sys

import fastkml

from kml import generate_kml


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s KML_FILE' % sys.argv[0])

    # Load user-provided KML file
    k = fastkml.kml.KML()
    with open(sys.argv[1], 'rb') as fh:
        k.from_string(fh.read())

    # Iterate over Document, Folder etc. to find features
    # TODO: Only support nested structure with a single Folder
    features = list(k.features())
    while True:
        try:
            features = list(features[0].features())
        except AttributeError:
            break

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

    generate_kml(
        invaders=working_invaders_to_flash,
        out_file='data/invaders-to-flash.kml',
        name='Invaders left to flash',
    )
    print('%s invaders left to flash!' % len(working_invaders_to_flash))
