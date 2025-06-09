import pytest
from unittest.mock import patch

from py_scripts.file_mapper.file_mapper import map_to_test_file

@pytest.mark.parametrize("test_case", [
    ("__pycache__/something.py", None),
    ("file.pyc", None),
    ("tests/test_utils.py", "tests/test_utils.py"),
])
def test_special_cases(test_case):
    """Test cases that don't require glob mocking (pycache, pyc, existing tests)."""
    input_file, expected = test_case
    assert map_to_test_file(input_file) == expected

@pytest.mark.parametrize("test_case", [
    # (input_file, glob_pattern, glob_returns, expected_output)
    (
        "utils.py",
        "tests/*/test_utils.py",
        ["tests/unit/test_utils.py"],
        "tests/unit/test_utils.py"
    ),
    (
        "models/user.py",
        "tests/*/test_models/test_user.py",
        ["tests/unit/test_models/test_user.py"],
        "tests/unit/test_models/test_user.py"
    ),
    (
        "api/v1/endpoints.py",
        "tests/*/test_api/test_v1/test_endpoints.py",
        ["tests/integration/test_api/test_v1/test_endpoints.py"],
        "tests/integration/test_api/test_v1/test_endpoints.py"
    ),
    # Test case where no matching test file exists
    (
        "utils.py",
        "tests/*test_utils.py",
        [],
        None
    ),
    # Multiple matches should return the first one
    (
        "common.py",
        "tests/*/test_common.py",
        [
            "tests/unit/test_common.py",
            "tests/integration/test_common.py"
        ],
        "tests/unit/test_common.py"
    ),
])
def test_glob_matches(test_case):
    """Test cases that require glob mocking."""
    input_file, expected_pattern, glob_returns, expected = test_case

    with patch('glob.glob') as mock_glob:
        mock_glob.return_value = glob_returns
        result = map_to_test_file(input_file)

        # Verify the result
        assert result == expected

        # Verify glob was called with correct pattern
        mock_glob.assert_called_with(expected_pattern)

def test_multiple_calls():
    """Test that the function works correctly when called multiple times."""
    with patch('glob.glob') as mock_glob:
        # First call
        mock_glob.return_value = ["tests/unit/test_a.py"]
        assert map_to_test_file("a.py") == "tests/unit/test_a.py"
        mock_glob.assert_called_with("tests/*/test_a.py")

        # Second call
        mock_glob.return_value = []
        assert map_to_test_file("b.py") is None
        mock_glob.assert_called_with("tests/*test_b.py")

        # Verify total number of calls
        assert mock_glob.call_count == 3

def test_nested_directory_structure():
    """Test handling of deeply nested directory structures."""
    with patch('glob.glob') as mock_glob:
        # Deep nesting
        mock_glob.return_value = ["tests/unit/test_deep/test_nested/test_file.py"]
        result = map_to_test_file("deep/nested/file.py")
        assert result == "tests/unit/test_deep/test_nested/test_file.py"
        mock_glob.assert_called_with("tests/*/test_deep/test_nested/test_file.py")
