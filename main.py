from collections import abc
import csv
import flask
import gzip
import io
import pathlib
import sqlite3
import typing
import templates

app = flask.Flask(__name__)
DATA_DIR = pathlib.Path('./data')
default_checked_waypoint_types = {
    'Boundary',
    'Bridge',
    'Campground',
    'Highway Jct',
    'Interstate Jct',
    'Lake',
    'Landmark',
    'Railroad Jct',
    'Trailhead',
    'Tunnel',
    'Water',
}


def get_db() -> sqlite3.Connection:
    db = getattr(flask.g, '_database', None)
    if db is None:
        uri = f'file:{DATA_DIR / "trail.db"}?mode=ro'
        db = flask.g._database = sqlite3.connect(uri, uri=True)
    return db


@app.teardown_appcontext
def close_connection(exception):
    _ = exception
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


class Point(typing.NamedTuple):
    lon: str
    lat: str
    ele: str


class Waypoint(typing.NamedTuple):
    name: str
    type: str
    comment: str
    lon: str
    lat: str
    ele: str

    def style(self) -> str:
        # style for KML
        return 'Water' if self.type == 'Water' else 'Other'


class Passage(typing.NamedTuple):
    passage: str
    name: str
    fname: str

    def formatted_name(self) -> str:
        return (
            f'{self.passage.lstrip("0")}: {self.name}'
            if self.passage
            else self.name
        )

    def style(self) -> str:
        # style for KML
        try:
            i = int(self.passage)
        except ValueError:
            return 'PA'
        if i == flagstaff_passage:
            return 'PA'
        elif i < flagstaff_passage:
            return 'P1' if i % 2 == 1 else 'P2'
        else:
            return 'P1' if i % 2 == 0 else 'P2'

    def track(self) -> abc.Iterator[Point]:
        with (DATA_DIR / self.fname).open('r') as f:
            for row in csv.reader(f):
                yield Point(*row)

    def waypoints(self, allow_types: set[str]) -> abc.Iterator[Waypoint]:
        if not self.passage:
            return

        for (
            type,
            name,
            notes,
            comment,
            ata_num,
            lon,
            lat,
            ele,
        ) in get_db().execute(
            """SELECT type, name, notes, comment, ata_num, lon, lat, ele FROM waypoints
            WHERE passage = ?""",
            (self.passage,),
        ):
            if not type in allow_types:
                continue

            # The following is an attempt to filter out waypoints with low
            # significance (example: junction with unnamed 2 track), and to
            # create better names and description.

            if type == 'Trailhead':
                name = name + ' Trailheaad'
            elif type in ('Road Jct', 'Highway Jct', 'Interstate Jct'):
                if not name or name == 'RJ':
                    continue
                name = f'RJ {name}'
            elif type == 'Trail Jct':
                if not name:
                    continue
                name = f'TJ {name}'
            elif type == 'Water':
                name, _, _ = name.partition('&')
                name = f'{name} {notes}'.strip()
            elif type == 'Milepost':
                name = ata_num
            elif type == 'Landmark':
                pass
            else:
                name = comment

            if not name:
                continue

            comment = comment.removeprefix(name)

            yield Waypoint(
                type=type,
                name=name,
                comment=comment,
                lon=lon,
                lat=lat,
                ele=ele,
            )


@app.route('/download')
def download():
    args = flask.request.args
    allowed_waypoint_types = set(
        waypoint_types[i]
        for i in args.getlist('wp', type=int)
        if i >= 0 and i < len(waypoint_types)
    )

    direction = lambda x: x
    if args.get('dir', default='NOBO') == 'SOBO':
        direction = lambda x: reversed(list(x))

    fmt_templates = dict(gpx=templates.gpx, kml=templates.kml)
    fmt = args.get('format', default='gpx')
    if fmt not in fmt_templates:
        flask.abort(400, description='Invalid format')

    start = args.get('start', type=int, default=1)
    if start < 1 or start > max_passage:
        flask.abort(400, description='Invalid passsage')

    end = args.get('end', type=int, default=0)
    if end <= 0:
        end = start - end
    elif end < start:
        end = start

    passages = [
        Passage(passage=passage, name=name, fname=fname)
        for passage, name, fname in get_db().execute(
            """SELECT passage, name, fname FROM passages
           WHERE
                passage GLOB '[0-9][0-9]'
                AND CAST(passage as INTEGER) >= ?
                AND CAST(passage as INTEGER) <= ?
           ORDER BY passage
           """,
            (start, end),
        )
    ]

    if len(passages) > max_passage:
        name = 'AZT'
        stem = 'azt'
    elif len(passages) == 1:
        name = f'AZT {passages[0].formatted_name()}'
        stem = f'passage-{passages[0].passage}'
    else:
        name = f'AZT Passages {passages[0].passage} - {passages[-1].passage}'
        stem = f'passage-{passages[0].passage}-{passages[-1].passage}'

    out = io.BytesIO()
    gz = gzip.open(out, encoding='utf-8', mode='wt')
    fmt_templates[fmt](
        gz.write,
        name=name,
        passages=passages,
        allowed_waypoint_types=allowed_waypoint_types,
        direction=direction,
    )
    gz.close()

    return flask.Response(
        out.getvalue(),
        mimetype='text/xml',
        headers={
            'Content-Disposition': f'attachment; filename="{stem}.{fmt}"',
            'Content-Encoding': 'gzip',
        },
    )


@app.route('/')
def root():
    # index, name, checked
    waypoints = [
        (
            i,
            name,
            name in default_checked_waypoint_types,
        )
        for i, name in enumerate(waypoint_types)
    ]
    passages = [
        Passage(passage=passage, name=name, fname='')
        for passage, name in get_db().execute(
            """SELECT passage, name FROM passages
               WHERE passage GLOB '[0-9][0-9]'
               ORDER BY passage"""
        )
    ]
    out = io.StringIO()
    templates.index(out.write, passages, waypoints)
    return out.getvalue()


with app.app_context():
    waypoint_types: list[str] = [
        r[0]
        for r in get_db().execute(
            'SELECT DISTINCT type FROM waypoints ORDER BY type'
        )
    ]
    flagstaff_passage = (
        get_db()
        .execute(
            """SELECT CAST(passage as integer) FROM passages
               WHERE name = 'Flagstaff'"""
        )
        .fetchone()[0]
    )
    max_passage = (
        get_db()
        .execute("""SELECT MAX(CAST(passage as integer)) FROM passages""")
        .fetchone()[0]
    )

if __name__ == '__main__':
    # Flask's development server automatically serves static files from /static.
    app.run(host='127.0.0.1', port=8080, debug=True)

