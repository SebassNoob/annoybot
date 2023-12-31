
.PHONY: run init_db drop_db test_db black migrate
.ONESHELL:

SHELL := bash

ifeq ($(version),)
	DC_CMD := docker compose -f docker-compose.dev.yml
else
	DC_CMD := docker compose -f docker-compose.$(version).yml
	tag := --$(version)
endif

# docker-compose
run:
	$(DC_CMD) -v down
	$(DC_CMD) up -d --build --remove-orphans

down:
	$(DC_CMD) -v down

# alembic
migrate:
	bash scripts/alembic_migration.sh $(tag)

revise:
	bash scripts/alembic_revision.sh $(name)

# misc commands to init and drop db manually
init_db:
	python db/init_db.py init $(tag)

drop_db:
	python db/init_db.py drop $(tag)

test_db:
	python db/init_db.py test $(tag)

# migrate from 1.9.0
migrate_1_9_0:
	bash scripts/major_migrate.sh
# black formatter
black:
	black ./src
	black ./db

