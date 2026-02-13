lint:
		uv run pre-commit run --all

run:
		uv run start-app

all:
		uv run pre-commit run --all
		uv run start-app

pyt:
		uv run pytest

cov:
		uv run pytest --cov=src --cov-report=term-missing

coverage:
		uv run pytest --cov=src --cov-report=term-missing --cov-report=html
