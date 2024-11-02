import pytest

# Assuming the original file is named test_mapper.py
from file_mapper import convert_filename, map_to_test_file

def test_convert_filename_simple():
    """Test simple filename conversion"""
    assert convert_filename("file.py") == "tests/test_file.py"

def test_convert_filename_with_path():
    """Test conversion of file with path"""
    assert convert_filename("src/utils/file.py") == "tests/test_src/test_utils/test_file.py"

def test_map_to_test_file_pycache():
    """Test mapping of __pycache__ files"""
    assert map_to_test_file("__pycache__/file.pyc") is None
    assert map_to_test_file("src/__pycache__/file.py") is None

def test_map_to_test_file_pyc():
    """Test mapping of .pyc files"""
    assert map_to_test_file("file.pyc") is None
    assert map_to_test_file("src/file.pyc") is None

def test_map_to_test_file_test_files():
    """Test mapping of existing test files"""
    test_file = "tests/test_file.py"
    assert map_to_test_file(test_file) == test_file

def test_map_to_test_file_source_files():
    """Test mapping of source files to test files"""
    assert map_to_test_file("file.py") == "tests/test_file.py"
    assert map_to_test_file("src/utils/file.py") == "tests/test_src/test_utils/test_file.py"

@pytest.fixture
def mock_subprocess(mocker):
    """Fixture to mock subprocess.run"""
    return mocker.patch('subprocess.run')

@pytest.fixture
def mock_print(mocker):
    """Fixture to mock print function"""
    return mocker.patch('builtins.print')

#def test_run_pytest_on_mapped_file_with_test(mock_subprocess, mock_print):
#    """Test running pytest on a valid mapped file"""
#    run_pytest_on_mapped_file("src/file.py")
#    mock_subprocess.assert_called_once_with(["pytest", "tests/test_src/test_file.py"])
#    mock_print.assert_called_once_with("Running tests for tests/test_src/test_file.py")
#
#def test_run_pytest_on_mapped_file_no_test(mock_subprocess, mock_print):
#    """Test running pytest on a file that doesn't map to a test"""
#    run_pytest_on_mapped_file("__pycache__/file.pyc")
#    mock_subprocess.assert_not_called()
#    mock_print.assert_called_once_with("No test file mapped for __pycache__/file.pyc. Skipping pytest.")
#
#def test_run_pytest_on_mapped_file_absolute_path(mock_subprocess, mock_print):
#    """Test running pytest with absolute path input"""
#    abs_path = os.path.abspath("src/file.py")
#    run_pytest_on_mapped_file(abs_path)
#    mock_subprocess.assert_called_once_with(["pytest", "tests/test_src/test_file.py"])
#    mock_print.assert_called_once_with("Running tests for tests/test_src/test_file.py")
