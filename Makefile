update-database: download aggregate-database

download:
	python3 con.py download

aggregate-seasons:
	python3 con.py aggregate-seasons

update-core:
	python3 con.py update-core

update-finished:
	python3 con.py update-finished

update-upcoming:
	python3 con.py update-upcoming

aggregate-database: aggregate-seasons update-core update-finished update-upcoming

find-games:
	python3 con.py find-games

find-new-games:
	python3 con.py find-new-games