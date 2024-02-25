# AZT Data

This project implements a web server for creating GPX and KML files from data
provided by the [Arizona Trail Association](https://aztrail.org).  The server
provides more options for the data included in the files than the files
provided directly by the trail association.

Build the data files used by the web server:

1. `python3 -m pip install pyshp`
2.  Download polylines and points from [AZGeo Data](https://azgeo-open-data-agic.hub.arcgis.com/search?q=Arizona%20National%20Scenic%20Trail).
3. Unzip the 7-zip archives.
4. `python3 build.py ./data polylinedir/commondata/new_azt_gpx_data_for_ata/AZT_Passages pointsdir/commondata/new_azt_gpx_data_for_ata/AZT_Waypoints`

Run the server:

1. `python3 -m pip install flask`
2. `python3 main.py`

Deploy the server to [App Engine](https://cloud.google.com/):

1. Download the Google Cloud command line utility and create an App Engine project.
2. `gcloud app deploy`.

