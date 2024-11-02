# Root Makefile


# Default target
.PHONY: all
all: file_mapper make_commit

.PHONY: file_mapper
file_mapper:
	$(MAKE) -C file_mapper

.PHONY: make_commit
make_commit:
	$(MAKE) -C make_commit
