# Root Makefile


# Default target
.PHONY: all
all: action_checker file_mapper make_commit webp_converter

.PHONY: action_checker
action_checker:
	$(MAKE) -C py_scripts/action_checker

.PHONY: file_mapper
file_mapper:
	$(MAKE) -C py_scripts/file_mapper

.PHONY: make_commit
make_commit:
	$(MAKE) -C py_scripts/make_commit

.PHONY: webp_converter
webp_converter:
	$(MAKE) -C py_scripts/webp_converter

.PHONY: install
install:
	ln -sf $(PWD)/webp_converter/webp_converter.py ~/.local/bin/webp_converter.py
	ln -sf $(PWD)/make_commit/make_commit.py ~/.local/bin/make_commit.py
	ln -sf $(PWD)/file_mapper/file_mapper.py ~/.local/bin/file_mapper.py

.PHONY: test
test:
	uv run pytest py_scripts/action_checker/tests/
	uv run pytest py_scripts/file_mapper/tests/
	uv run pytest py_scripts/make_commit/tests/
	uv run pytest py_scripts/webp_converter/tests/
