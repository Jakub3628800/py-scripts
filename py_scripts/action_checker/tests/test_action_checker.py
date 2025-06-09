from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import action_checker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module by loading the action_checker.py file directly
import importlib.util
spec = importlib.util.spec_from_file_location("action_checker_module",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "action_checker.py"))
action_checker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(action_checker_module)


def test_notification_msg():
    pr_checks = [
        {"name": "test1", "result": "success", "url": "https://github.com/user/repo/check/123"},
        {"name": "test2", "result": "failure", "url": "https://github.com/user/repo/check/456"}
    ]
    result = action_checker_module.notification_msg(pr_checks)
    expected = "\nPR checks finished for repo\ntest1: success\ntest2: failure"
    assert result == expected


def test_notification_msg_no_valid_url():
    pr_checks = [
        {"name": "test1", "result": "success", "url": "invalid"},
        {"name": "test2", "result": "failure", "url": "also/invalid"}
    ]
    result = action_checker_module.notification_msg(pr_checks)
    expected = "\nPR checks finished for \ntest1: success\ntest2: failure"
    assert result == expected


def test_dt_diff():
    dt1 = "2023-01-01T12:30:00Z"
    dt2 = "2023-01-01T12:00:00Z"
    result = action_checker_module.dt_diff(dt1, dt2)
    assert result == "0:30:00"


@patch.object(action_checker_module, 'subprocess')
def test_pr_checker_success(mock_subprocess):
    mock_output = [
        {
            "name": "test1",
            "state": "SUCCESS",
            "link": "https://github.com/user/repo/check/123",
            "startedAt": "2023-01-01T12:00:00Z",
            "completedAt": "2023-01-01T12:30:00Z"
        }
    ]
    mock_result = MagicMock()
    mock_result.stdout = json.dumps(mock_output)
    mock_subprocess.run.return_value = mock_result

    result = action_checker_module.pr_checker()

    assert len(result) == 1
    assert result[0]["name"] == "test1"
    assert result[0]["result"] == "SUCCESS"
    assert result[0]["duration"] == "0:30:00"


@patch.object(action_checker_module, 'pr_checker')
@patch.object(action_checker_module, 'subprocess')
@patch.object(action_checker_module, 'time')
def test_monitor_checks_success(mock_time, mock_subprocess, mock_pr_checker):
    # First call returns in-progress checks, second call returns completed
    mock_pr_checker.side_effect = [
        [{"name": "test1", "result": "IN_PROGRESS", "url": "https://github.com/user/repo/check/123", "duration": "0:01:00"}],
        [{"name": "test1", "result": "SUCCESS", "url": "https://github.com/user/repo/check/123", "duration": "0:01:00"}]
    ]

    result = action_checker_module.monitor_checks()

    assert result == 0
    assert mock_pr_checker.call_count == 2
    assert mock_time.sleep.call_count == 1
    mock_subprocess.call.assert_called_once()


@patch.object(action_checker_module, 'pr_checker')
def test_monitor_checks_exception(mock_pr_checker):
    mock_pr_checker.side_effect = Exception("Test error")

    with patch('builtins.print') as mock_print:
        result = action_checker_module.monitor_checks()

    assert result == 1
    mock_print.assert_called_once_with("Error: Test error")


@patch.object(action_checker_module, 'setup_systemd_service')
def test_main_default(mock_setup):
    with patch('sys.argv', ['action_checker.py']):
        result = action_checker_module.main()

    assert result == 0
    mock_setup.assert_called_once()


@patch.object(action_checker_module, 'monitor_checks')
def test_main_monitor_flag(mock_monitor):
    mock_monitor.return_value = 0

    with patch('sys.argv', ['action_checker.py', '--monitor']):
        result = action_checker_module.main()

    assert result == 0
    mock_monitor.assert_called_once()
