install:
	poetry install

style: install
	poetry run isort federatedmlrest
	poetry run flake8 federatedmlrest
	poetry run mypy -p federatedmlrest
	poetry run pydocstyle federatedmlrest

run: install
	poetry run python -m federatedmlrest.main