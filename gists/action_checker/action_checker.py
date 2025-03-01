class ActionChecker:
    def __init__(self):
        self.actions = []
        
    def add_action(self, action):
        """Add an action to be checked"""
        self.actions.append(action)
        
    def check_actions(self):
        """Check all registered actions"""
        results = []
        for action in self.actions:
            results.append(self._check_action(action))
        return results
        
    def _check_action(self, action):
        """Internal method to check a single action"""
        # Basic validation logic
        if not isinstance(action, dict):
            return False
        if 'type' not in action:
            return False
        return True