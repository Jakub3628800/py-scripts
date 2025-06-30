# CMD Picker

Unified command picker that combines functionality from tmux-picker, docker-picker, and gh-picker into one general-purpose tool.

## Features

- **Multiple Tools**: Support for tmux, docker, and GitHub CLI
- **Interactive Interface**: Terminal UI with vim-style navigation
- **Live Preview**: See details and content for selected items
- **Tool-specific Actions**: Each tool has custom actions (delete, start/stop, merge, etc.)
- **Unified Experience**: Same interface across all tools

## Usage

### Show available tools
```bash
cmd-picker
```

### Use specific tools
```bash
# Tmux session picker
cmd-picker tmux

# Docker container picker
cmd-picker docker

# GitHub pull request picker
cmd-picker gh
```

### Direct execution
```bash
# One-time execution
uvx --from git+https://github.com/Jakub3628800/py-scripts cmd-picker tmux

# After installation
uv tool install git+https://github.com/Jakub3628800/py-scripts
cmd-picker docker
```

## Supported Tools

### Tmux (`cmd-picker tmux`)
- **Purpose**: Interactive tmux session browser
- **Actions**:
  - Enter: Attach to session
  - d: Delete session
- **Preview**: Session info, window list, and content preview
- **Requirements**: tmux

### Docker (`cmd-picker docker`)
- **Purpose**: Docker container management
- **Actions**:
  - Enter: Exec into running container or start stopped container
  - s: Start/stop container
  - l: View logs
- **Preview**: Container details and recent logs
- **Requirements**: docker

### GitHub (`cmd-picker gh`)
- **Purpose**: GitHub pull request browser
- **Actions**:
  - Enter: Open PR in browser
  - c: Checkout PR locally
  - m: Merge PR
- **Preview**: PR details, commits, and changed files
- **Requirements**: gh CLI

## Controls

Universal controls across all tools:
- `j` / `↓` - Move down
- `k` / `↑` - Move up
- `Enter` - Execute primary action
- `q` - Quit

Additional tool-specific controls are shown in the interface.

## Architecture

The tool uses a plugin-based architecture with a base `Tool` class that each implementation extends:

- **TmuxTool**: Handles tmux session management
- **DockerTool**: Manages docker containers
- **GhTool**: Interfaces with GitHub CLI

New tools can be easily added by implementing the `Tool` interface.

## Examples

```bash
# Show all available tools and their status
cmd-picker

# Pick and attach to a tmux session
cmd-picker tmux

# Manage docker containers interactively
cmd-picker docker

# Browse and interact with GitHub PRs
cmd-picker gh
```

## Requirements

- Python 3.8+
- Tool-specific requirements:
  - tmux (for tmux functionality)
  - docker (for docker functionality)
  - gh CLI (for GitHub functionality)
