.PHONY: all test watch

# Default target
all: test

# Run tests with verbose output
test:
	uv run pytest -v

# Watch for changes in Python files and run action_checker.py
watch:
	find . -type f -name "*.py" | entr -p python action_checker.py /_
