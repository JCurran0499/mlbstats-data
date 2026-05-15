LAMBDAS     := $(filter-out shared,$(notdir $(wildcard lambdas/*)))
TARGETS     := $(if $(LAMBDA),$(LAMBDA),$(LAMBDAS))
ECR_REGISTRY := 298451523862.dkr.ecr.us-east-1.amazonaws.com

STACK   ?=
TAG     := $(shell git rev-parse --short HEAD)-$(shell date +%s)
LAMBDA  ?=

.PHONY: build push atlas-dev deploy-db deploy

# Required: STACK — the CloudFormation template filename (without .yaml) and stack name suffix to deploy
deploy:
ifndef STACK
	$(error STACK is required, e.g. make deploy STACK=ecr)
endif
	aws cloudformation deploy \
		--template-file infra/$(STACK).yaml \
		--stack-name mlbstats-$(STACK) \
		--capabilities CAPABILITY_NAMED_IAM

atlas-dev:
	docker start atlas-dev || docker run -d --name atlas-dev -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=dev -p 5432:5432 postgres:17

deploy-db:
	atlas schema apply --env prod --to file://schema.sql

# Optional: LAMBDA — restricts the build to a single lambda; omit to build all lambdas
build:
	for lambda in $(TARGETS); do \
		pipenv requirements > lambdas/$$lambda/requirements.txt; \
		docker build --platform linux/amd64 --provenance=false -f lambdas/$$lambda/Dockerfile -t $$lambda lambdas/; \
		rm lambdas/$$lambda/requirements.txt; \
	done

# Required: LAMBDA — the lambda image to tag and push to ECR
# Optional: TAG — the image tag to apply; defaults to the current git short SHA + Unix timestamp
push:
ifndef LAMBDA
	$(error LAMBDA is required, e.g. make push LAMBDA=roster_sync)
endif
	aws ecr get-login-password --region us-east-1 | \
		docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker tag $(LAMBDA) $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)
	docker push $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)
	aws ssm put-parameter \
		--name /mlbstats/lambdas/$(subst _,-,$(LAMBDA))/image-tag \
		--value $(TAG) \
		--type String \
		--overwrite
	@echo "Pushed $(ECR_REGISTRY)/mlbstats/$(subst _,-,$(LAMBDA)):$(TAG)"
