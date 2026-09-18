.PHONY: install test lint train all
PYTHON ?= python3

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

train:
	$(PYTHON) -m pip install -r requirements-training.txt
	$(PYTHON) train_model.py

all: lint test
