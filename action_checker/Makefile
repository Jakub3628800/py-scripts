.PHONY: test symlink check-deps

check-deps:
        @if ! command -v gh &> /dev/null; then \
                echo "Error: GitHub CLI (gh) is not installed"; \
                exit 1; \
        fi
        @gh --version

test:
        python3 -m unittest test_action_checker.py

symlink: check-deps
        @echo "Checking dependencies before creating symlink..."
        ln -sf $(PWD)/action_checker.py /usr/local/bin/action_checker
        @echo "Symlink created successfully"