# Action Checker

Monitors GitHub PR checks and sends notifications when complete.

## Usage

### Directly from GitHub (no cloning required):
```bash
uvx --from git+https://github.com/Jakub3628800/py-scripts action-checker
```

### From cloned repository:
```bash
uv run py-scripts/action_checker/action_checker.py
```

## Prerequisites

- `gh` CLI tool configured with authentication
- `notify-send` for desktop notifications
- Must be run from a directory with an open GitHub PR

## Features

- Monitors PR check status in real-time
- Creates systemd user service for background monitoring
- Sends desktop notification when all checks complete
- Automatic retry logic for network issues
