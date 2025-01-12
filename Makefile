test:
	poetry run pytest --tb=short

watch-tests:
	ls *.py | entr poetry run pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')
