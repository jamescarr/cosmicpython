
# Make "help" the default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | awk 'BEGIN {FS = ":.*##"}; { printf "\033[36m%-20s\033[0m %s\n", $$1, $$2 }'

test:  ## Run the tests using Poetry and pytest
	poetry run pytest

watch-tests:  ## Run tests continuously using pytest-watch
	poetry run ptw .

black:  ## Run black on the project
	poetry run black -l 86 $$(find * -name '*.py')

api-dev:  ## Runs the API Server
	poetry run fastapi dev cosmicpython/api.py
