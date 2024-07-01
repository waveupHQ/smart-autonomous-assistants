.PHONY: install test lint format clean

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	pylint **/*.py

format:
	black .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
