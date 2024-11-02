import os
import sys
import subprocess
from typing import List, Optional


def convert_filename(filename: str) -> str:
    """Convert a source file name to its corresponding test file path."""
    all_parts: List[str] = filename.split("/")
    all_parts = [f"test_{part}" for part in all_parts]
    return f"tests/{'/'.join(all_parts)}".strip("\n")


def map_to_test_file(changed_file: str) -> Optional[str]:
    """Map a source file to its corresponding test file, if applicable."""
    if "__pycache__" in changed_file or changed_file.endswith(".pyc"):
        return None
    elif changed_file.startswith("tests"):
        return changed_file
    else:
        return convert_filename(changed_file)


def run_pytest_on_mapped_file(changed_file: str) -> None:
    """Run pytest on the mapped test file, if applicable."""
    # Convert to a relative path if it's an absolute path
    relative_changed_file = os.path.relpath(changed_file)

    # Map to corresponding test file
    mapped_test_file = map_to_test_file(relative_changed_file)

    # Only run pytest if there’s a mapped test file
    if mapped_test_file:
        print(f"Running tests for {mapped_test_file}")
        subprocess.run(["pytest", mapped_test_file])
    else:
        print(f"No test file mapped for {changed_file}. Skipping pytest.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <changed_file>")
        sys.exit(1)

    # Get the changed file from the command line arguments
    changed_file = sys.argv[1]
    run_pytest_on_mapped_file(changed_file)
