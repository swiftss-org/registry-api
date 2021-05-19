COMPOSE_ENV = "local"

help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  dep             to install dependencies."
	@echo "  pre-commit      to run the pre-commit checks."
	@echo "  build           to build the stack in docker compose."
	@echo "  run             to run the stack in docker compose."
	@echo "  migrate         to run the DB migrations in docker compose."
	@echo "  test            to run the stack tests in docker compose."
	@echo "  cover           to print the code coverage in docker compose."
	@echo "  teardown        to tear down the stack in docker compose."

dep:
	pip install -r requirements/${COMPOSE_ENV}.txt

pre-commit:
	pre-commit run --all-files

build:
	docker-compose -f ${COMPOSE_ENV}.yml build

run: build
	docker-compose -f ${COMPOSE_ENV}.yml up -d

migrate:
	docker-compose -f ${COMPOSE_ENV}.yml exec -T django bash -c "python manage.py makemigrations && python manage.py migrate"

test:
	docker-compose -f ${COMPOSE_ENV}.yml exec -T django coverage run --rcfile=.pre-commit/setup.cfg -m pytest --disable-pytest-warnings;

cover:
	docker-compose -f ${COMPOSE_ENV}.yml exec -T django coverage report

teardown:
	docker-compose -f ${COMPOSE_ENV}.yml down -v
