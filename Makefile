.IGNORE:
SHELL = /bin/bash

default: all

all:

dist: _dists_updated _tars_updated theme1

_dists_updated: _dist theme1
	./create_themes.sh
	echo "all dist updated" > _dists_updated

_tars_updated: _dist theme1
	./pack_tars.sh
	echo "all tars updated" > _tars_updated

clean:
	./clean_themes.sh

