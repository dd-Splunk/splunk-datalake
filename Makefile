.SILENT:
.PHONY: up logs down clean
DC := docker compose
SHELL := /bin/bash 

up:
	rm -rf ./deployment-apps/README
	date +"Now time is %FT%T%z"
	$(DC) up -d
	date +"Now time is %FT%T%z"

logs:
	$(DC) logs -f
down:
	$(DC) down
	rm -rf ./deployment-apps/README
clean:
	$(DC) down -v
	rm -rf ./deployment-apps/README