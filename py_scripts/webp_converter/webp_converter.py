# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pillow",
# ]
# ///

import argparse
import sys
from pathlib import Path

from PIL import Image


def convert_webp_to_jpg(input_path_str: str, output_path_str: str | None = None) -> None:
    """
    Convert a WebP image to JPG format.
    Args:
        input_path_str (str): Path to input WebP file.
        output_path_str (str, optional): Path for output JPG file. If not provided,
                                     will save to current directory.
    Raises:
        FileNotFoundError: If the input file doesn't exist.
        IOError: If there's an error reading or writing the image.
        ValueError: If the input file is not a valid image.
    """
    input_path = Path(input_path_str)

    if output_path_str:
        output_path = Path(output_path_str)
    else:
        output_path = Path.cwd() / f"{input_path.stem}.jpg"

    try:
        img = Image.open(input_path)
    except FileNotFoundError:
        raise  # Reraise FileNotFoundError to be caught by main
    except IOError as e:
        raise ValueError(f"Invalid or corrupt image file: {input_path}") from e

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGB")

    try:
        img.save(output_path, "JPEG", quality=95)
        print(f"Successfully converted {input_path} to {output_path}")
    except IOError as e:
        raise IOError(f"Error saving output file: {output_path}") from e


def main() -> int:
    """Entry point for the webp-converter command-line tool."""
    parser = argparse.ArgumentParser(description="Convert WebP images to JPG format")
    parser.add_argument("input", help="Input WebP file path")
    parser.add_argument("-o", "--output", help="Output JPG file path (optional)", default=None)

    args = parser.parse_args()

    try:
        convert_webp_to_jpg(args.input, args.output)
        return 0
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
