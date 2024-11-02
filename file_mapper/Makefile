.PHONY: test watch

test:
	pytest -v

watch:
	find . -type f -name "*.py" | entr -p python file_mapper.py /_
