#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import subprocess
import sys
import argparse
import re


def extract_unit_name(systemd_run_output: str) -> str | None:
    """
    Extract the unit name from systemd-run output.

    Output typically looks like:
    "Running as unit: run-u12345.service"
    or
    "Running as unit run-u12345.service"
    """
    match = re.search(r"Running as unit:?\s+(\S+\.service)", systemd_run_output)
    if match:
        return match.group(1)
    return None


def run_durable_command(command: list[str], unit_name: str | None = None) -> int:
    """
    Run a command using systemd-run and follow its logs.

    Args:
        command: The command to run as a list of arguments
        unit_name: Optional custom unit name

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Build systemd-run command
    systemd_cmd = ["systemd-run", "--user", "--pty"]

    if unit_name:
        systemd_cmd.extend(["--unit", unit_name])

    systemd_cmd.append("--")
    systemd_cmd.extend(command)

    # Start the service
    try:
        result = subprocess.run(
            systemd_cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"Error starting service: {result.stderr}", file=sys.stderr)
            return 1

        # Extract unit name from output
        unit = extract_unit_name(result.stderr)

        if not unit:
            # Try stdout as fallback
            unit = extract_unit_name(result.stdout)

        if not unit:
            print("Error: Could not determine unit name from systemd-run output", file=sys.stderr)
            print(f"Output: {result.stderr}", file=sys.stderr)
            return 1

    except FileNotFoundError:
        print("Error: systemd-run not found. Is systemd available?", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running systemd-run: {e}", file=sys.stderr)
        return 1

    print(f"Started service: {unit}")
    print("Following logs (Ctrl+C to detach)...\n")

    # Follow logs with journalctl
    journalctl_cmd = ["journalctl", "--user", "-f", "-u", unit]

    try:
        # Run journalctl and let it stream to stdout
        # We don't capture output here, let it go directly to the terminal
        subprocess.run(journalctl_cmd, check=False)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n" + "=" * 70)
        print("DETACHED FROM LOGS")
        print("=" * 70)
        print(f"\nThe service '{unit}' is still running in the background.")
        print("\nTo view logs again:")
        print(f"  journalctl --user -f -u {unit}")
        print("\nTo stop the service:")
        print(f"  systemctl --user stop {unit}")
        print("\nTo check service status:")
        print(f"  systemctl --user status {unit}")
        print("=" * 70)

    return 0


def main() -> int:
    """Entry point for the durable-run command-line tool."""
    parser = argparse.ArgumentParser(
        description="Run a command as a systemd user service and follow its logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with a command that prints every second
  durable-run bash -c 'while true; do date; sleep 1; done'

  # Run a web server
  durable-run python -m http.server 8080

  # With custom unit name
  durable-run --unit my-counter -- bash -c 'i=0; while true; do echo "Count: $i"; i=$((i+1)); sleep 1; done'

The command will run in the background as a systemd user service.
Press Ctrl+C to detach from logs (the service keeps running).
        """,
    )

    parser.add_argument(
        "--unit",
        help="Custom unit name for the service",
        default=None,
    )

    parser.add_argument(
        "command",
        nargs="+",
        help="Command to run",
    )

    args = parser.parse_args()

    return run_durable_command(args.command, args.unit)


if __name__ == "__main__":
    sys.exit(main())
