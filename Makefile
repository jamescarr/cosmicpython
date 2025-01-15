
# Make "help" the default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | awk 'BEGIN {FS = ":.*##"}; { printf "\033[36m%-20s\033[0m %s\n", $$1, $$2 }'

test:  ## Run the tests using Poetry and pytest
	uv run pytest

watch-tests:  ## Run tests continuously using pytest-watch
	uv run ptw .

black:  ## Run black on the project
	uv run black -l 86 $$(find * -name '*.py')

api-dev: install ## Runs the API Server
	uv run fastapi dev cosmicpython/endpoints/api.py

clean:  ## Wipe out venv, docker, etc.
	rm -rf .venv

install:  ## install dependencies
	uv pip install -r pyproject.toml
