update-database: download aggregate-database

download:
	python3 service.py download

aggregate-seasons:
	python3 service.py aggregate-seasons

update-core:
	python3 service.py update-core

update-finished:
	python3 service.py update-finished

update-upcoming:
	python3 service.py update-upcoming

aggregate-database: aggregate-seasons update-core update-finished update-upcoming

find-games:
	python3 service.py find-games

find-new-games:
	python3 service.py find-new-games