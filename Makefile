
.PHONY: run init_db drop_db test_db black

run:
	echo "Running db and bot..."
	docker compose -v down
	docker compose build
	docker compose up -d
	

init_db:
	python db/init_db.py init

drop_db:
	python db/init_db.py drop

test_db:
	python db/init_db.py test

black:
	black ./src
	black ./db

