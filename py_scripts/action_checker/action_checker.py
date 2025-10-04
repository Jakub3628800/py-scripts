# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import json.decoder
import time
import subprocess
from typing import TypedDict, List
import json
import os
from datetime import datetime
from pathlib import Path


class Check(TypedDict):
    name: str
    result: str
    duration: str
    url: str


def notification_msg(pr_checks: List[Check]) -> str:
    repository_name = ""
    for check in pr_checks:
        try:  # find repository name
            repository_name = check["url"].split("/")[4]
            break
        except IndexError:
            continue

    return f"\nPR checks finished for {repository_name}\n" + "\n".join(
        [f"{i['name']}: {i['result']}" for i in pr_checks]
    )


def dt_diff(dt1: str, dt2: str) -> str:
    return str(datetime.strptime(dt1, "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(dt2, "%Y-%m-%dT%H:%M:%SZ"))


def pr_checker() -> List[Check]:
    """Returns list of PR checks."""

    for _ in range(0, 10):
        try:
            result = subprocess.run(
                ["gh", "pr", "checks", "--json=name,state,link,startedAt,completedAt"],
                capture_output=True,
                text=True,
                check=True,
            )
            output = json.loads(result.stdout)
            return [
                {
                    "name": c["name"],
                    "result": c["state"],
                    "url": c["link"],
                    "duration": dt_diff(c["completedAt"], c["startedAt"]),
                }
                for c in output
            ]

        except subprocess.CalledProcessError as e:
            if "no pull request found" in e.stderr.lower():
                raise SystemExit(1, "No pull request found in current directory")
            time.sleep(1)
            continue
        except json.decoder.JSONDecodeError:
            time.sleep(1)
            continue

    raise SystemExit(1, "Cannot parse gh pr checks output")


def setup_systemd_service() -> None:
    """Create and start a systemd user service to monitor PR checks."""
    script_path = os.path.abspath(__file__)
    service_content = f"""[Unit]
Description=GitHub PR Check Monitor
After=network.target

[Service]
Type=oneshot
RemainAfterExit=no
Environment=HOME={os.environ["HOME"]}
Environment=PATH=/home/{os.environ.get("USER", "user")}/.local/bin:/usr/local/bin:/usr/bin:/bin
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/env uv run {script_path} --monitor
TimeoutStartSec=1800
StandardOutput=journal
StandardError=journal
"""

    # Create systemd user directory
    systemd_dir = Path.home() / ".config" / "systemd" / "user"
    systemd_dir.mkdir(parents=True, exist_ok=True)

    # Write service file
    service_file = systemd_dir / "pr-check-monitor.service"
    service_file.write_text(service_content)

    # Check if there's a PR first
    try:
        subprocess.run(["gh", "pr", "view", "--json=url"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        print("No pull request found in current directory")
        print("Navigate to a directory with an open PR before running this script")
        return

    # Reload daemon only if needed and start service
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(
        ["systemctl", "--user", "start", "--no-block", "pr-check-monitor.service"],
        check=True,
    )

    print("Monitoring PR checks in background...")
    print("View logs: journalctl --user -u pr-check-monitor.service -f")


def monitor_checks() -> int:
    """Monitor PR checks and send notification when done."""
    try:
        pr_checks = pr_checker()
        while {"IN_PROGRESS", "QUEUED"}.intersection([i["result"] for i in pr_checks]):
            pr_checks = pr_checker()
            time.sleep(3)

        subprocess.call(["notify-send", notification_msg(pr_checks)])
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


def main() -> int:
    """Entry point for the action-checker command-line tool."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        return monitor_checks()
    else:
        setup_systemd_service()
        return 0


if __name__ == "__main__":
    exit(main())
