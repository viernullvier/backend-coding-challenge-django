.PHONY: build start test migrate format

build:
	docker-compose build

start:
	docker-compose up

test:
	docker-compose run --rm app sh -c "python manage.py test && flake8"

migrate:
	docker-compose run --rm app sh -c "python manage.py migrate"

format:
	docker-compose run --rm app sh -c "black -l 79 ."
