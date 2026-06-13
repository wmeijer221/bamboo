build_run: build run

build:
	poetry build
	pip install ./dist/bamboo-0.0.1.tar.gz

lint:
	# Runs black checker
	poetry run black --check bamboo tests
	# Runs flake8 using the config file
	poetry run flake8 bamboo tests --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 bamboo tests --count --exit-zero --statistics

profile:
	poetry run pytest tests --profile-svg

test:
	poetry run pytest .
