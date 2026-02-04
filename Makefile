lint:
		uv run pre-commit run --all

run:
		uv run main.py

all:
		uv run pre-commit run --all
		uv run main.py
