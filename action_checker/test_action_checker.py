import unittest
from unittest.mock import patch, MagicMock
from action_checker import notification_msg, dt_diff, pr_checker

class TestActionChecker(unittest.TestCase):
    def test_notification_msg(self):
        checks = [
            {"name": "test1", "result": "SUCCESS", "url": "https://github.com/org/repo/pull/1"},
            {"name": "test2", "result": "FAILURE", "url": "https://github.com/org/repo/pull/1"}
        ]
        expected = "\nPR checks finished for repo\ntest1: SUCCESS\ntest2: FAILURE"
        self.assertEqual(notification_msg(checks), expected)

    def test_dt_diff(self):
        dt1 = "2023-01-01T12:00:00Z"
        dt2 = "2023-01-01T11:00:00Z"
        self.assertEqual(dt_diff(dt1, dt2), "1:00:00")

    @patch('subprocess.getoutput')
    def test_pr_checker(self, mock_getoutput):
        mock_data = [
            {
                "name": "test1",
                "state": "SUCCESS",
                "link": "https://example.com",
                "startedAt": "2023-01-01T12:00:00Z",
                "completedAt": "2023-01-01T12:30:00Z"
            }
        ]
        mock_getoutput.return_value = json.dumps(mock_data)
        
        result = pr_checker()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test1")
        self.assertEqual(result[0]["result"], "SUCCESS")

if __name__ == '__main__':
    unittest.main()