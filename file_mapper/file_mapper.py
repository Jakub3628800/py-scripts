"""Map file to test files to be used for inotify running tests."""

import sys
from typing import List, Optional


def convert_filename(filename: str) -> str:
    all_: List[str] = filename.split("/")
    all_ = [f"test_{i}" for i in all_]
    all_ = "/".join(all_)
    return f"tests/{all_}".strip("\n")


def main(argv: List[str]) -> Optional[str]:
    try:
        line: str = argv[1]
        if "__pycache__" in line or ".pyc" in line:
            return None
        elif line.startswith("tests"):
            return line
        else:
            return convert_filename(line)
    except IndexError:
        # No argument provided
        return None
    except EOFError:
        # No more information
        return None


if __name__ == "__main__":
    #print("running")
    result: Optional[str] = main(sys.argv)
    if result:
        print(result)
    pass
