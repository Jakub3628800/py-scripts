import pytest
import os
from PIL import Image
import tempfile
import shutil
from webp_converter import convert_webp_to_jpg

class TestWebPConverter:
    @pytest.fixture
    def setup_test_files(self):
        # Create a temporary directory for test files
        test_dir = tempfile.mkdtemp()

        # Create a test WebP image
        test_image = Image.new('RGB', (100, 100), color='red')
        test_webp_path = os.path.join(test_dir, 'test.webp')
        test_image.save(test_webp_path, 'WEBP')

        # Create a test WebP image with transparency
        test_image_rgba = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        test_webp_transparent_path = os.path.join(test_dir, 'test_transparent.webp')
        test_image_rgba.save(test_webp_transparent_path, 'WEBP')

        yield {
            'test_dir': test_dir,
            'test_webp': test_webp_path,
            'test_webp_transparent': test_webp_transparent_path
        }

        # Cleanup after tests
        shutil.rmtree(test_dir)

    def test_basic_conversion(self, setup_test_files):
        """Test basic WebP to JPG conversion"""
        input_path = setup_test_files['test_webp']
        output_path = os.path.join(setup_test_files['test_dir'], 'output.jpg')

        convert_webp_to_jpg(input_path, output_path)

        # Verify the output file exists
        assert os.path.exists(output_path)
        # Verify it's a valid JPEG
        with Image.open(output_path) as img:
            assert img.format == 'JPEG'

    def test_transparent_conversion(self, setup_test_files):
        """Test conversion of WebP with transparency"""
        input_path = setup_test_files['test_webp_transparent']
        output_path = os.path.join(setup_test_files['test_dir'], 'output_transparent.jpg')

        convert_webp_to_jpg(input_path, output_path)

        # Verify the output file exists
        assert os.path.exists(output_path)
        # Verify it's a valid JPEG and has been converted to RGB
        with Image.open(output_path) as img:
            assert img.format == 'JPEG'
            assert img.mode == 'RGB'

    def test_default_output_path(self, setup_test_files):
        """Test conversion with default output path"""
        input_path = setup_test_files['test_webp']

        # Save current working directory
        original_cwd = os.getcwd()
        os.chdir(setup_test_files['test_dir'])

        try:
            convert_webp_to_jpg(input_path)

            # Expected output filename
            expected_output = os.path.join(os.getcwd(), 'test.jpg')

            # Verify the output file exists
            assert os.path.exists(expected_output)
            # Verify it's a valid JPEG
            with Image.open(expected_output) as img:
                assert img.format == 'JPEG'
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def test_nonexistent_input(self):
        """Test handling of nonexistent input file"""
        with pytest.raises(FileNotFoundError):
            convert_webp_to_jpg('nonexistent.webp')

    def test_invalid_input_format(self, tmp_path):
        """Test handling of invalid input format"""
        # Create a text file instead of an image
        invalid_file = tmp_path / "invalid.webp"
        invalid_file.write_text("This is not an image")

        with pytest.raises(ValueError):
            convert_webp_to_jpg(str(invalid_file))

    def test_output_quality(self, setup_test_files):
        """Test that output JPEG has the expected quality setting"""
        input_path = setup_test_files['test_webp']
        output_path = os.path.join(setup_test_files['test_dir'], 'output_quality.jpg')

        convert_webp_to_jpg(input_path, output_path)

        # Read the output file size
        output_size = os.path.getsize(output_path)

        # Create a low quality version for comparison
        low_quality_path = os.path.join(setup_test_files['test_dir'], 'low_quality.jpg')
        with Image.open(input_path) as img:
            img.save(low_quality_path, 'JPEG', quality=50)

        low_quality_size = os.path.getsize(low_quality_path)

        # The higher quality output should be larger than the low quality version
        assert output_size > low_quality_size
