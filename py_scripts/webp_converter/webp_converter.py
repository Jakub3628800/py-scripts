# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pillow",
# ]
# ///

from PIL import Image
import os
import argparse

def convert_webp_to_jpg(input_path: str, output_path: str | None = None) -> None:
    """
    Convert a WebP image to JPG format
    Args:
        input_path (str): Path to input WebP file
        output_path (str, optional): Path for output JPG file. If not provided,
                                   will save to current directory
    Raises:
        FileNotFoundError: If the input file doesn't exist
        IOError: If there's an error reading or writing the image
        ValueError: If the input file is not a valid image
    """
    # Check if input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # If output path not provided, use current directory
    if output_path is None:
        # Get just the filename without path
        filename = os.path.basename(input_path)
        # Replace .webp extension with .jpg
        jpg_filename = os.path.splitext(filename)[0] + '.jpg'
        # Save to current directory
        output_path = os.path.join(os.getcwd(), jpg_filename)

    # Open and convert the image
    try:
        img = Image.open(input_path)
    except IOError as e:
        raise ValueError(f"Invalid or corrupt image file: {input_path}") from e

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGB')

    # Save as JPG
    try:
        img.save(output_path, 'JPEG', quality=95)
        print(f"Successfully converted {input_path} to {output_path}")
    except IOError as e:
        raise IOError(f"Error saving output file: {output_path}") from e

def main() -> int:
    """Entry point for the webp-converter command-line tool."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert WebP images to JPG format')
    parser.add_argument('input', help='Input WebP file path')
    parser.add_argument('-o', '--output', help='Output JPG file path (optional)', default=None)

    # Parse arguments
    args: argparse.Namespace = parser.parse_args()

    # Convert the image
    try:
        convert_webp_to_jpg(args.input, args.output)
        return 0
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
