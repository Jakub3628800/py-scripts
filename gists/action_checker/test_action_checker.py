import unittest
from action_checker import ActionChecker

class TestActionChecker(unittest.TestCase):
    def setUp(self):
        self.checker = ActionChecker()
        
    def test_valid_action(self):
        action = {'type': 'valid_action'}
        self.checker.add_action(action)
        results = self.checker.check_actions()
        self.assertTrue(all(results))
        
    def test_invalid_action_missing_type(self):
        action = {'name': 'invalid_action'}
        self.checker.add_action(action)
        results = self.checker.check_actions()
        self.assertFalse(all(results))
        
    def test_invalid_action_wrong_type(self):
        action = 'not_a_dict'
        self.checker.add_action(action)
        results = self.checker.check_actions()
        self.assertFalse(all(results))
        
    def test_multiple_actions(self):
        actions = [
            {'type': 'valid1'},
            {'type': 'valid2'},
            {'name': 'invalid'}
        ]
        for action in actions:
            self.checker.add_action(action)
        results = self.checker.check_actions()
        self.assertEqual(results, [True, True, False])

if __name__ == '__main__':
    unittest.main()