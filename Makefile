.DEFAULT_GOAL := all
isort = isort api tests
black = black -S -l 120 --target-version py38 api tests

.PHONY: up
up:
	docker-compose up

.PHONY: up-d
up-d:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: build
build:
	docker-compose build

.PHONY: format
format:
	docker-compose run api $(isort)
	docker-compose run api $(black)

.PHONY: schema
schema:
	docker-compose run api python api/models/management/generate_schema.py

.PHONY: test
test:
	docker-compose exec api pytest tests

.PHONY: pre-post
pre-post:
	docker-compose run catalog-trigger python /app/triggers/management/change_streams_pre_and_post.py
