# Build data files for the application. The data files are:
#
#   trail.db - SQLlite database with passages and waypoints tables.
#   *.csv - Track as a CSV file with lon, lat, and ele fields.

import shapefile
import csv
import pathlib
import sqlite3
import sys

# db column name, db column type, record field name
passage_columns = [
    ('passage', 'text', 'Passage'),
    ('name', 'text', 'Name'),
    ('miles', 'real', 'Miles'),
    ('sort', 'integer', 'Sort'),
    ('id', 'integer', 'ID'),
    ('calc_length', 'real', 'Calc_Lengt'),
    ('weblink', 'text', 'Weblink'),
    ('shape_length', 'real', 'Shape_Leng'),
    ('mp_name', 'text', 'MP_Name'),
    ('fname', 'text', None),
]

waypoint_columns = [
    ('type', 'text', 'Type'),
    ('name', 'text', 'Name'),
    ('ata_num', 'text', 'ATA_Num'),
    ('notes', 'text', 'Notes'),
    ('comment', 'text', 'Comment'),
    ('passage', 'text', 'Passage'),
    ('ata_num_ol', 'text', 'ATA_Num_ol'),
    ('ata_number', 'integer', 'ATA_Number'),
    ('letter', 'text', 'Letter'),
    ('mp', 'real', 'MP'),
    ('waypnt_id ', '', 'Waypnt_ID'),
    ('lat', 'real', None),
    ('lon', 'real', None),
    ('ele', 'real', None),
]


def create_table_statement(columns, table: str) -> str:
    return f'CREATE TABLE {table} ({", ".join(f"{n} {t}" for n, t, _ in columns)})'


def insert_statement(columns, table: str) -> str:
    return f'INSERT INTO {table} values({", ".join(["?"] * len(columns))})'


def column_index(columns, name: str) -> int:
    for i, (n, _, _) in enumerate(columns):
        if n == name:
            return i
    assert False, f'column {name} not found'


def run(
    dst: pathlib.Path, passage_src: pathlib.Path, waypoints_src: pathlib.Path
):
    dst.mkdir(exist_ok=True)
    (dst / 'trail.db').unlink(missing_ok=True)

    con = sqlite3.connect(dst / 'trail.db')

    con.execute(create_table_statement(passage_columns, 'passages'))

    stmt = insert_statement(passage_columns, 'passages')
    fname_index = column_index(passage_columns, 'fname')
    with shapefile.Reader(passage_src) as sf:
        shapes = sf.shapes()
        for i, r in enumerate(sf.records()):
            fname = r['Name'].replace(' ', '').replace("'", '') + '.csv'
            data = [r[c] if c else None for _, _, c in passage_columns]
            data[fname_index] = fname
            with con:
                con.execute(stmt, data)
            with (dst / fname).open('w') as f:
                w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                for (lon, lat), ele in zip(shapes[i].points, shapes[i].z):
                    w.writerow((lon, lat, ele))

    con.execute(create_table_statement(waypoint_columns, 'waypoints'))
    con.execute('CREATE INDEX waypoint_passage ON waypoints ( passage )')

    stmt = insert_statement(waypoint_columns, 'waypoints')
    lon_index = column_index(waypoint_columns, 'lon')
    lat_index = column_index(waypoint_columns, 'lat')
    ele_index = column_index(waypoint_columns, 'ele')
    with shapefile.Reader(waypoints_src) as sf:
        shapes = sf.shapes()
        for i, r in enumerate(sf.records()):
            data = [r[c] if c else None for _, _, c in waypoint_columns]
            (lon, lat) = shapes[i].points[0]
            ele = shapes[i].z[0]
            data[lon_index] = lon
            data[lat_index] = lat
            data[ele_index] = ele
            with con:
                con.execute(stmt, data)

    con.close()


run(
    pathlib.Path(sys.argv[1]),
    pathlib.Path(sys.argv[2]),
    pathlib.Path(sys.argv[3]),
)
