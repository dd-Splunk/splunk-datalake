.PHONY: up down clean
SHELL := /bin/bash 

up:
	rm -rf ./deployment-apps/README
	docker compose up -d ds1

down:
	docker compose down
clean:
	docker compose down -v