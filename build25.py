# Repair Passage 25. The data on AZGeo Data Hub is garbled.
#
# 1. Download GPX file from https://aztrail.org/explore/passages/
#
# 2. python3 build25.py ./data dir/pass.gpx

import csv
import pathlib
import sys
import xml.etree.ElementTree as ET


def run(dst, src):

    root = ET.fromstring(src.read_text())
    with (dst / 'WhiterockMessage.csv').open('w') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for i, trk in enumerate(
            root.findall('{http://www.topografix.com/GPX/1/1}trk')
        ):
            for trkseg in trk.findall(
                '{http://www.topografix.com/GPX/1/1}trkseg'
            ):
                trkpts = trkseg.findall(
                    '{http://www.topografix.com/GPX/1/1}trkpt'
                )
                if i == 0:
                    # First track is SOBO!
                    trkpts = reversed(trkpts)
                for trkpt in trkpts:
                    e = trkpt.find('{http://www.topografix.com/GPX/1/1}ele')
                    ele = e.text if e is not None else ''
                    row = (trkpt.get('lat', ''), trkpt.get('lon', ''), ele)
                    w.writerow(row)


run(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
