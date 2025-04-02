# Root Makefile


# Default target
.PHONY: all
all: file_mapper make_commit webp_converter

.PHONY: file_mapper
file_mapper:
	$(MAKE) -C file_mapper

.PHONY: make_commit
make_commit:
	$(MAKE) -C make_commit

.PHONY: webp_converter
webp_converter:
	$(MAKE) -C webp_converter

.PHONY: install
install:
	ln -sf $(PWD)/webp_converter/webp_converter.py ~/.local/bin/webp_converter.py
	ln -sf $(PWD)/make_commit/make_commit.py ~/.local/bin/make_commit.py
	ln -sf $(PWD)/file_mapper/file_mapper.py ~/.local/bin/file_mapper.py

.PHONY: test
test:
	python3 -m pytest py-scripts/file_mapper/tests/
	python3 -m pytest py-scripts/make_commit/tests/
	python3 -m pytest py-scripts/webp_converter/tests/
