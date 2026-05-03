LAMBDAS := $(filter-out shared,$(notdir $(wildcard lambdas/*)))

.PHONY: requirements build atlas-dev deploy-db

atlas-dev:
	docker start atlas-dev || docker run -d --name atlas-dev -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=dev -p 5432:5432 postgres:17

deploy-db:
	atlas schema apply --env prod --to file://schema/schema.sql

requirements:
	for lambda in $(LAMBDAS); do \
		pipenv requirements > lambdas/$$lambda/requirements.txt; \
	done

build:
	for lambda in $(LAMBDAS); do \
		docker build -f lambdas/$$lambda/Dockerfile -t $$lambda lambdas/; \
	done

