.PHONY: build start test

build:
	docker-compose build

start:
	docker-compose up

test:
	docker-compose run --rm app sh -c "python manage.py test && flake8"
