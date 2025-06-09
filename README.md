# Python Scripts Collection

Collection of standalone Python utilities for development workflows.

## Available Scripts

- **tmux-picker**: Interactive tmux session browser with live preview
- **action-checker**: Monitor GitHub PR checks via gh CLI
- **webp-converter**: Convert WebP images to JPG
- **file-mapper**: Map source files to test files for hot-reload

## Usage

### One-time execution (uvx)
Run scripts individually without installing:

```bash
# Tmux session picker
uvx --from git+https://github.com/Jakub3628800/py-scripts tmux-picker

# GitHub action checker
uvx --from git+https://github.com/Jakub3628800/py-scripts action-checker

# WebP converter
uvx --from git+https://github.com/Jakub3628800/py-scripts webp-converter input.webp
```

### Persistent installation (uv tool)
For repeated use, install as tools to avoid reconfiguring dependencies:

```bash
# Install all scripts as persistent tools
uv tool install git+https://github.com/Jakub3628800/py-scripts

# Now run directly (faster, deps cached)
tmux-picker
action-checker
webp-converter input.webp
```

## Prerequisites

- **tmux-picker**: tmux
- **action-checker**: gh CLI
- **file-mapper**: entr
- **clipboardtools**: wl-clipboard, fzf
