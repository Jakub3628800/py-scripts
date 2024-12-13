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
	$(MAKE) -C webp_converter symlink
