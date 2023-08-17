PAAS_PASSWORD_STORE_DIR?=${HOME}/.paas-pass

POETRY := $(shell which poetry)
$(if $(POETRY),,$(error "poetry not found"))

CF := $(shell which cf)
$(if $(CF),,$(error "cf not found"))

MANIFEST_FILE:=manifest.yml
APP_NAME := $(shell poetry run python3 -c 'import yaml; f=open("$(MANIFEST_FILE)"); manifest=yaml.safe_load(f); print(manifest["applications"][0]["name"])')
$(if $(APP_NAME),,$(error ERROR: manifest.yaml must specify an application name))
BUCKET_NAME := $(shell poetry run python3 -c 'import yaml; f=open("$(MANIFEST_FILE)"); manifest=yaml.safe_load(f); print(manifest["applications"][0]["services"][0])')
$(if $(BUCKET_NAME),,$(error ERROR: manifest.yaml must contain a services section with an S3 bucket name))

.PHONY: deploy
deploy: check-bucket-exists load-and-check-secrets requirements.txt
	@$(CF) push \
		--var github_client_id=${GITHUB_CLIENT_ID} \
		--var github_client_secret=${GITHUB_CLIENT_SECRET} \
		--var secret_key=${SECRET_KEY}

.PHONY: load-and-check-secrets
load-and-check-secrets: github-secrets app-secrets
	$(if $(GITHUB_CLIENT_ID),,$(error ERROR: GITHUB_CLIENT_ID not set))
	$(if $(GITHUB_CLIENT_SECRET),,$(error ERROR: GITHUB_CLIENT_SECRET not set))
	$(if $(SECRET_KEY),,$(error ERROR: SECRET_KEY not set))
	@true

.PHONY: github-secrets
github-secrets:
	$(eval export GITHUB_CLIENT_ID?=$(shell PASSWORD_STORE_DIR=$(PAAS_PASSWORD_STORE_DIR) pass github.com/unlucky-dip/client_id))
	$(eval export GITHUB_CLIENT_SECRET?=$(shell PASSWORD_STORE_DIR=$(PAAS_PASSWORD_STORE_DIR) pass github.com/unlucky-dip/client_secret))
	@true

.PHONY: app-secrets
app-secrets:
	$(if \
		$(shell cf env $(APP_NAME) 2>/dev/null | grep SECRET_KEY), \
		$(eval export SECRET_KEY?=$(shell cf env $(APP_NAME) | grep SECRET_KEY | cut -d: -f2 | tr -d ' ')), \
		$(eval export SECRET_KEY?=$(shell poetry run python3 -c 'import secrets; print(secrets.token_urlsafe(32))')) \
			$(info INFO: generated new 32 character SECRET_KEY) \
	)
	@true

.PHONY: check-bucket-exists
check-bucket-exists:
	$(if \
		$(shell cf service $(BUCKET_NAME) | grep '^broker:' | awk '{print $2}'), \
		@true, \
		$(error ERROR: bucket $(BUCKET_NAME) does not exist) \
	)


requirements.txt: poetry.lock
	@$(POETRY) export -f requirements.txt -o requirements.txt
	$(info INFO: local requirements.txt updated)
