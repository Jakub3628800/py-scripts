#!/usr/bin/env python3

import pytest
from unittest.mock import Mock, patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from py_scripts.durable_run.durable_run import extract_unit_name, run_durable_command


class TestExtractUnitName:
    def test_extract_with_colon(self):
        output = "Running as unit: run-u12345.service"
        result = extract_unit_name(output)
        assert result == "run-u12345.service"

    def test_extract_without_colon(self):
        output = "Running as unit run-u67890.service"
        result = extract_unit_name(output)
        assert result == "run-u67890.service"

    def test_extract_with_multiline(self):
        output = "Some other text\nRunning as unit: my-custom-service.service\nMore text"
        result = extract_unit_name(output)
        assert result == "my-custom-service.service"

    def test_extract_no_match(self):
        output = "This is some random output without a unit"
        result = extract_unit_name(output)
        assert result is None

    def test_extract_empty_string(self):
        output = ""
        result = extract_unit_name(output)
        assert result is None


class TestRunDurableCommand:
    @patch("subprocess.run")
    def test_successful_run(self, mock_run):
        # Mock systemd-run success, then journalctl interrupted
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr="Running as unit: run-u12345.service"),
            KeyboardInterrupt(),  # journalctl interrupted by Ctrl+C
        ]

        result = run_durable_command(["echo", "hello"])

        # Should handle KeyboardInterrupt gracefully and return 0
        assert result == 0

        # Verify systemd-run was called
        assert mock_run.call_count == 2
        first_call = mock_run.call_args_list[0]
        assert "systemd-run" in first_call[0][0]
        assert "--user" in first_call[0][0]
        assert "echo" in first_call[0][0]
        assert "hello" in first_call[0][0]

        # Verify journalctl was called
        second_call = mock_run.call_args_list[1]
        assert "journalctl" in second_call[0][0]
        assert "--user" in second_call[0][0]
        assert "-f" in second_call[0][0]
        assert "run-u12345.service" in second_call[0][0]

    @patch("subprocess.run")
    def test_systemd_run_failure(self, mock_run):
        # Mock systemd-run failure
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error: permission denied")

        result = run_durable_command(["echo", "hello"])

        assert result == 1

    @patch("subprocess.run")
    def test_systemd_run_not_found(self, mock_run):
        # Mock systemd-run not found
        mock_run.side_effect = FileNotFoundError()

        result = run_durable_command(["echo", "hello"])

        assert result == 1

    @patch("subprocess.run")
    def test_custom_unit_name(self, mock_run):
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr="Running as unit: my-service.service"),
            KeyboardInterrupt(),
        ]

        result = run_durable_command(["sleep", "10"], unit_name="my-service")

        assert result == 0

        # Verify --unit was passed
        first_call = mock_run.call_args_list[0]
        assert "--unit" in first_call[0][0]
        assert "my-service" in first_call[0][0]

    @patch("subprocess.run")
    def test_unit_name_from_stdout(self, mock_run):
        # Sometimes systemd-run outputs to stdout instead of stderr
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Running as unit: run-u99999.service", stderr=""),
            KeyboardInterrupt(),
        ]

        result = run_durable_command(["date"])

        assert result == 0
        # Should still work
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_no_unit_name_found(self, mock_run):
        # systemd-run succeeds but we can't find the unit name
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="Some unexpected output")

        result = run_durable_command(["echo", "test"])

        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])
