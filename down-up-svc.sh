#!/bin/bash
SVC=$1

docker compose stop ${SVC} && docker compose rm -f -v ${SVC} && docker compose up -d ${SVC}