.PHONY: up logs down clean
DC := docker compose
SHELL := /bin/bash 

up:
	rm -rf ./deployment-apps/README
	$(DC) up -d
logs:
	$(DC) logs -f
down:
	$(DC) down
clean:
	$(DC) down -v