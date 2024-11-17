from PIL import Image
import os
import argparse

def convert_webp_to_jpg(input_path, output_path=None):
    """
    Convert a WebP image to JPG format

    Args:
        input_path (str): Path to input WebP file
        output_path (str, optional): Path for output JPG file. If not provided,
                                   will save to current directory
    """
    try:
        # Open the WebP image
        img = Image.open(input_path)

        # If output path not provided, use current directory
        if output_path is None:
            # Get just the filename without path
            filename = os.path.basename(input_path)
            # Replace .webp extension with .jpg
            jpg_filename = os.path.splitext(filename)[0] + '.jpg'
            # Save to current directory
            output_path = os.path.join(os.getcwd(), jpg_filename)

        # Convert and save as JPG
        # If image has transparency, convert to RGB first
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGB')

        img.save(output_path, 'JPEG', quality=95)
        print(f"Successfully converted {input_path} to {output_path}")

    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert WebP images to JPG format')
    parser.add_argument('input', help='Input WebP file path')
    parser.add_argument('-o', '--output', help='Output JPG file path (optional)', default=None)

    # Parse arguments
    args = parser.parse_args()

    # Convert the image
    convert_webp_to_jpg(args.input, args.output)
