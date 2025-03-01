.PHONY: test clean

test:
	@echo "Running tests..."
	@python3 -m unittest discover -v

clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

format:
	@echo "Formatting code..."
	@black .

lint:
	@echo "Linting code..."
	@flake8 .