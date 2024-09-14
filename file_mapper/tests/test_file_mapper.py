import pytest
from file_mapper import convert_filename, main

def test_convert_filename():
    assert convert_filename("src/module/file.py") == "tests/unit/test_src/test_module/test_file.py"
    assert convert_filename("file.py") == "tests/unit/test_file.py"
    assert convert_filename("deeply/nested/path/file.py") == "tests/unit/test_deeply/test_nested/test_path/test_file.py"

@pytest.mark.parametrize("input_arg, expected_output", [
    (["script.py", "src/module/file.py"], "tests/unit/test_src/test_module/test_file.py"),
    (["script.py", "tests/unit/test_file.py"], "tests/unit/test_file.py"),
    (["script.py", "__pycache__/file.pyc"], None),
    (["script.py"], None),
])
def test_main(input_arg, expected_output):
    assert main(input_arg) == expected_output

def test_main_eof_error(monkeypatch):
    def mock_argv():
        raise EOFError()

    monkeypatch.setattr("sys.argv", mock_argv)
    assert main([]) is None
