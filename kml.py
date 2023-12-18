import fastkml
from pygeoif.geometry import Point


def _compute_color(invader):
    """
    Compute KML color based on invader points and status.
    """
    if invader['status_description'] == 'OK':
        if int(invader['points']) == 100:
            return 'purple'
        elif int(invader['points']) == 50:
            return 'pink'
    elif invader['status_description'] in ['Détruit !', 'Non visible']:
        return 'red'
    elif invader['status_description'] in ['Dégradé', 'Très dégradé']:
        return 'brown'
    return 'yellow'


def generate_kml(
    invaders,
    out_file,
    name,
):
    """
    Generate a GPX file from all known invaders with their locations.
    """
    kml = fastkml.kml.KML()

    ns = '{http://www.opengis.net/kml/2.2}'
    d = fastkml.kml.Document(
        ns,
        name=name,
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

    for invader in invaders:
        if not invader['lat'] and not invader['lon']:
            # No GPS coordinates
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
