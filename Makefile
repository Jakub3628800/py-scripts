# Root Makefile

.PHONY: install
install:
	uv pip install -e .

.PHONY: test
test:
	uv run pytest py_scripts/*/tests/ -v

.PHONY: all
all: install
