# TMUX Session Picker

Interactive tmux session browser with live preview and vim-style navigation.

## Features

- 🚀 Colorful terminal interface with emoji indicators
- 📺 Live session content preview - see what's happening in each session
- ⌨️ Vim-style navigation (j/k or arrow keys)
- 🗑️ Session deletion with confirmation prompt
- 📋 Session info display (windows, creation time)

## Usage

1. Run directly with uv:
```bash
uv run py-scripts/tmux_picker/tmux_picker.py
```

2. Or install the package and use the command:
```bash
uv pip install -e .
tmux-picker
```

## Controls

- `j` / `↓` - Move down
- `k` / `↑` - Move up
- `Enter` - Attach to selected session
- `d` - Delete session (with Y/N confirmation)
- `q` - Quit

## Example

```bash
# Create some test sessions
tmux new-session -d -s "work"
tmux new-session -d -s "coding"
tmux new-session -d -s "monitoring"

# Launch the picker
tmux-picker
```

The interface shows:
- Session list with highlighted selection
- Live preview of the selected session's current content
- Session metadata (window count, creation time)

## Requirements

- Python 3.8+
- tmux
