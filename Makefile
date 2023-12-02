.SILENT:
.PHONY: up logs down clean
DC := docker compose
SHELL := /bin/bash

up:
	rm -rf ./deployment-apps/README
	date +"Now time is %FT%T%z"
	$(DC) up --build -d
	date +"Now time is %FT%T%z"

logs:
	$(DC) logs -f
down:
	$(DC) down

clean:
	$(DC) down -v
