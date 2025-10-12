# Durable Run

A thin wrapper around `systemd-run` that automatically follows logs and provides clear instructions when detaching.

## Features

- **Background Execution**: Runs commands as systemd user services
- **Automatic Log Following**: Immediately starts tailing logs after starting the service
- **Graceful Detach**: Ctrl+C detaches from logs without stopping the service
- **Clear Instructions**: Shows exactly how to reconnect to logs or stop the service
- **Custom Unit Names**: Optional custom naming for easier service management

## Usage

### Basic usage
```bash
# Test with a command that prints every second (easy to see it working)
durable-run bash -c 'while true; do date; sleep 1; done'

# Run a counter that increments every second
durable-run bash -c 'i=0; while true; do echo "Count: $i"; i=$((i+1)); sleep 1; done'

# Run a web server
durable-run python -m http.server 8080

# Run a long-running process
durable-run sleep 3600
```

### With custom unit name
```bash
durable-run --unit my-web-server -- python -m http.server 8080
```

### Direct execution
```bash
# One-time execution
uvx --from git+https://github.com/Jakub3628800/py-scripts durable-run sleep 60

# After installation
uv tool install git+https://github.com/Jakub3628800/py-scripts
durable-run sleep 60
```

## How it works

1. Starts your command as a systemd user service using `systemd-run --user`
2. Extracts the service unit name from systemd output
3. Immediately starts following logs with `journalctl --user -f -u <unit>`
4. When you press Ctrl+C:
   - Detaches from logs (service keeps running)
   - Displays the unit name
   - Shows commands to:
     - View logs again: `journalctl --user -f -u <unit>`
     - Stop the service: `systemctl --user stop <unit>`
     - Check status: `systemctl --user status <unit>`

## Example session

```bash
$ durable-run bash -c 'i=0; while true; do echo "Count: $i"; i=$((i+1)); sleep 1; done'
Started service: run-u12345.service
Following logs (Ctrl+C to detach)...

Count: 0
Count: 1
Count: 2
Count: 3
Count: 4
^C

======================================================================
DETACHED FROM LOGS
======================================================================

The service 'run-u12345.service' is still running in the background.

To view logs again:
  journalctl --user -f -u run-u12345.service

To stop the service:
  systemctl --user stop run-u12345.service

To check service status:
  systemctl --user status run-u12345.service
======================================================================
```

## Prerequisites

- systemd (Linux systems with systemd)
- journalctl (typically included with systemd)

## Use cases

- Running development servers in the background
- Starting long-running processes without tmux/screen
- Quick testing of services with automatic log viewing
- Development workflows where you need processes to persist after detaching

## Differences from `systemd-run` alone

- **Automatic log following**: No need to manually run `journalctl`
- **Clear exit message**: Shows exactly what to do after Ctrl+C
- **Convenience**: One command instead of two (systemd-run + journalctl)
- **Better UX**: User-friendly output and instructions
