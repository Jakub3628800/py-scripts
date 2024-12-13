.PHONY: all test watch

# Default target
all: test

# Run tests with verbose output
test:
	uv run pytest -v

# Symlink webp_converter.py to ~/.local/bin
symlink:
	ln -sf $(PWD)/webp_converter/webp_converter.py ~/.local/bin/webp_converter.py

# Watch for changes in Python files and run file_mapper.py
watch:
	find . -type f -name "*.py" | entr -p python file_mapper.py /_
