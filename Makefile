LAMBDAS := $(notdir $(wildcard lambdas/*))

.PHONY: requirements build

requirements:
	for lambda in $(LAMBDAS); do \
		pipenv requirements > lambdas/$$lambda/requirements.txt; \
	done

