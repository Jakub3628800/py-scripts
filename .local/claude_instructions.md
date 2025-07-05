# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a collection of standalone Python scripts organized as utilities. Each script is self-contained with its own dependencies managed through uv script headers.

## Development Commands

**Testing:**
- Run all tests: `make test` or `uv run pytest py-scripts/file_mapper/tests/ py-scripts/make_commit/tests/ py-scripts/webp_converter/tests/`
- Test individual modules: `cd py-scripts/{module} && make test`

**Build/Install:**
- Install scripts to ~/.local/bin: `make install`
- Build all modules: `make all`

## Key Utilities

**file_mapper**: Maps source files to corresponding test files, supports watch mode with `entr`
**action_checker**: Monitors GitHub PR checks via gh CLI
**make_commit**: Creates commits via GitHub API using environment variables (GH_TOKEN, GH_USERNAME, GH_REPO)
**webp_converter**: Converts WebP images to JPG using Pillow
**clipboardtools**: Wayland clipboard history with fzf search
**s2t**: Speech-to-text transcription using OpenAI API
**tmux_picker**: Interactive tmux session browser with live preview and vim-style navigation

## Script Dependencies

Scripts use uv script headers for dependency management. Prerequisites:
- file_mapper: `entr`
- action_checker: `gh` CLI
- clipboardtools: `wl-clipboard`, `fzf`
- tmux_picker: `tmux`

## Environment Variables

**make_commit** requires:
- `GH_TOKEN`: GitHub API token
- `GH_USERNAME`: GitHub username (default: "Jakub3628800")
- `GH_REPO`: Repository name (default: "entroppy")
- `MAIN_BRANCH`: Branch name (default: "master")