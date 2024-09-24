
.PHONY: serve
serve:
	python3 main.py

.PHONY: build
build:
	python3 build.py ./data/ \
		$(HOME)/Downloads/Arizona_National_Scenic_Trail_Polylines/commondata/new_azt_gpx_data_for_ata/AZT_Passages \
		$(HOME)/Downloads/Arizona_National_Scenic_Trail_Points/commondata/new_azt_gpx_data_for_ata/AZT_Waypoints
