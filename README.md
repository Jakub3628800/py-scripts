# py-scripts

Collection of standalone misc Python scripts.

## Available Scripts

- **cmd-picker**: Interactive command picker for tmux, docker, and gh request (scroll with jk + preview)
- **action-checker**: invoke on opening PR, get a success/fail notification when actions finish running
- **webp-converter**: webp to jpg cli
- **file-mapper**: map source files to test files
    - for hotreloading
- **durable-run**: wrapper around systemd-run that follows logs and provides clear detach instructions

## Usage

### One-time execution (uvx)
Run scripts individually without installing:

```sh
uvx --from git+https://github.com/Jakub3628800/py-scripts cmd-picker tmux
```
```sh
uvx --from git+https://github.com/Jakub3628800/py-scripts action-checker
```

```sh
uvx --from git+https://github.com/Jakub3628800/py-scripts webp-converter input.webp
```

```sh
uvx --from git+https://github.com/Jakub3628800/py-scripts durable-run bash -c 'while true; do date; sleep 1; done'
```

### Persistent installation (uv tool)
For repeated use, install as tools to avoid reconfiguring dependencies:

```bash
uv tool install git+https://github.com/Jakub3628800/py-scripts
```
After installing uv tool, all of the scripts should be in your path.

## Prerequisites

- **cmd-picker**: tmux, docker, gh CLI (depending on tool used)
- **action-checker**: gh CLI
- **file-mapper**: entr
- **clipboardtools**: wl-clipboard, fzf
- **durable-run**: systemd, journalctl
