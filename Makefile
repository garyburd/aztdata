
.PHONY: serve
serve:
	python3 main.py

.PHONY: build
build:
	python3 build.py ./data/ $(HOME)/Downloads/poly/commondata/new_azt_gpx_data_for_ata/AZT_Passages $(HOME)/Downloads/points/commondata/new_azt_gpx_data_for_ata/AZT_Waypoints
	python3 build25.py ./data/ $(HOME)/Downloads/fix/pass_25_new.gpx


