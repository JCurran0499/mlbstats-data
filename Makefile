LAMBDAS     := $(filter-out shared,$(notdir $(wildcard lambdas/*)))
TARGETS     := $(if $(LAMBDA),$(LAMBDA),$(LAMBDAS))
ECR_REGISTRY := 298451523862.dkr.ecr.us-east-1.amazonaws.com

STACK   ?=
TAG     ?= $(shell git rev-parse --short HEAD)
LAMBDA  ?=

.PHONY: build push atlas-dev deploy-db deploy-stack

deploy-stack:
ifndef STACK
	$(error STACK is required, e.g. make deploy-stack STACK=ecr)
endif
	aws cloudformation deploy \
		--template-file infra/$(STACK).yaml \
		--stack-name mlbstats-$(STACK) \
		--capabilities CAPABILITY_NAMED_IAM \
		$(if $(filter lambdas,$(STACK)),--parameter-overrides RosterSyncImageTag=$(TAG))

atlas-dev:
	docker start atlas-dev || docker run -d --name atlas-dev -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=dev -p 5432:5432 postgres:17

deploy-db:
	atlas schema apply --env prod --to file://schema/schema.sql

build:
	for lambda in $(TARGETS); do \
		pipenv requirements > lambdas/$$lambda/requirements.txt; \
		docker build --platform linux/amd64 --provenance=false -f lambdas/$$lambda/Dockerfile -t $$lambda lambdas/; \
		rm lambdas/$$lambda/requirements.txt; \
	done

push:
ifndef LAMBDA
	$(error LAMBDA is required, e.g. make push LAMBDA=roster_sync)
endif
	aws ecr get-login-password --region us-east-1 | \
		docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker tag $(LAMBDA) $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)
	docker push $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)
	@echo "Pushed $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)"
