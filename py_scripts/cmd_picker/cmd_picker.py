#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import subprocess
import sys
import os
import shutil
import termios
import tty
import json
import webbrowser
import argparse
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class Tool(ABC):
    """Base class for all tools"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_items(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_item_display(self, item: Dict[str, Any], selected: bool) -> str:
        pass

    @abstractmethod
    def get_item_preview(self, item: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def execute_action(self, item: Dict[str, Any]) -> None:
        pass

    def get_additional_actions(self) -> Dict[str, str]:
        """Return additional key bindings and their descriptions"""
        return {}

    def handle_additional_action(self, key: str, item: Dict[str, Any]) -> bool:
        """Handle additional actions. Return True if action was handled."""
        return False

    def can_create_new(self) -> bool:
        """Return True if this tool supports creating new items"""
        return False

    def create_new_item(self) -> bool:
        """Create a new item. Return True if items should be refreshed."""
        return False


class TmuxTool(Tool):
    @property
    def name(self) -> str:
        return "tmux"

    @property
    def description(self) -> str:
        return "Interactive tmux session picker"

    def is_available(self) -> bool:
        return shutil.which("tmux") is not None

    def get_items(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ['tmux', 'list-sessions', '-F', '#{session_name}\t#{session_windows}\t#{session_created}'],
                capture_output=True, text=True, check=True
            )
            items = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        items.append({
                            'name': parts[0],
                            'windows': parts[1],
                            'created': parts[2],
                            'type': 'session'
                        })
            return items
        except subprocess.CalledProcessError:
            return []

    def get_item_display(self, item: Dict[str, Any], selected: bool) -> str:
        if selected:
            return f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}📺 {item['name']}{Colors.RESET} {Colors.DIM}({item['windows']} windows){Colors.RESET}"
        else:
            return f"{Colors.BRIGHT_CYAN}📺 {item['name']}{Colors.RESET} {Colors.DIM}({item['windows']} windows){Colors.RESET}"

    def get_item_preview(self, item: Dict[str, Any]) -> str:
        try:
            # Get session info
            session_info = subprocess.run(
                ['tmux', 'display-message', '-t', item['name'], '-p',
                 '#{session_name}: #{session_windows} windows, created #{session_created}'],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get window list
            windows = subprocess.run(
                ['tmux', 'list-windows', '-t', item['name'], '-F',
                 '#{window_index}: #{window_name} #{?window_active,(active),}'],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get preview of active window
            preview = subprocess.run(
                ['tmux', 'capture-pane', '-t', item['name'], '-p'],
                capture_output=True, text=True, check=True
            ).stdout

            return f"{Colors.CYAN}{session_info}{Colors.RESET}\n\n{Colors.YELLOW}Windows:{Colors.RESET}\n{Colors.GREEN}{windows}{Colors.RESET}\n\n{Colors.YELLOW}Preview:{Colors.RESET}\n{preview[:500]}..."
        except subprocess.CalledProcessError:
            return f"{Colors.RED}Unable to get info for session: {item['name']}{Colors.RESET}"

    def execute_action(self, item: Dict[str, Any]) -> None:
        subprocess.run(['tmux', 'attach-session', '-t', item['name']])

    def get_additional_actions(self) -> Dict[str, str]:
        return {'d': 'Delete session', 'a': 'New session'}

    def handle_additional_action(self, key: str, item: Dict[str, Any]) -> bool:
        if key == 'd':
            print(f"\n{Colors.RED}Delete session '{item['name']}'? (y/N): {Colors.RESET}", end='', flush=True)
            confirm = sys.stdin.read(1)
            if confirm.lower() == 'y':
                try:
                    subprocess.run(['tmux', 'kill-session', '-t', item['name']], check=True)
                    return True
                except subprocess.CalledProcessError:
                    pass
        elif key == 'a':
            return self.create_new_item()
        return False

    def can_create_new(self) -> bool:
        return True

    def create_new_item(self) -> bool:
        print(f"\n{Colors.CYAN}Enter new session name: {Colors.RESET}", end='', flush=True)
        # Temporarily restore terminal settings to read input
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            session_name = input().strip()
            if session_name:
                try:
                    subprocess.run(['tmux', 'new-session', '-d', '-s', session_name], check=True)
                    print(f"{Colors.GREEN}✓ Session '{session_name}' created{Colors.RESET}")
                    return True
                except subprocess.CalledProcessError:
                    print(f"{Colors.RED}✗ Failed to create session '{session_name}'{Colors.RESET}")
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            tty.setraw(sys.stdin.fileno())
        return False


class DockerTool(Tool):
    @property
    def name(self) -> str:
        return "docker"

    @property
    def description(self) -> str:
        return "Interactive docker container picker"

    def is_available(self) -> bool:
        return shutil.which("docker") is not None

    def get_items(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}'],
                capture_output=True, text=True, check=True
            )
            items = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        items.append({
                            'id': parts[0][:12],
                            'name': parts[1],
                            'status': parts[2],
                            'image': parts[3],
                            'type': 'container'
                        })
            return items
        except subprocess.CalledProcessError:
            return []

    def get_item_display(self, item: Dict[str, Any], selected: bool) -> str:
        status_color = Colors.GREEN if 'Up' in item['status'] else Colors.RED
        if selected:
            return f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}🐳 {item['name']}{Colors.RESET} {Colors.DIM}({item['id']}){Colors.RESET} {status_color}{item['status']}{Colors.RESET}"
        else:
            return f"{Colors.BRIGHT_CYAN}🐳 {item['name']}{Colors.RESET} {Colors.DIM}({item['id']}){Colors.RESET} {status_color}{item['status']}{Colors.RESET}"

    def get_item_preview(self, item: Dict[str, Any]) -> str:
        try:
            # Get container details
            info_result = subprocess.run(
                ['docker', 'inspect', '--format',
                 '{{.Name}}: {{.Config.Image}}\nStatus: {{.State.Status}}\nCreated: {{.Created}}\nPorts: {{range $p, $conf := .NetworkSettings.Ports}}{{$p}}->{{(index $conf 0).HostPort}} {{end}}',
                 item['id']],
                capture_output=True, text=True, check=True
            )

            # Get recent logs
            logs_result = subprocess.run(
                ['docker', 'logs', '--tail', '20', item['id']],
                capture_output=True, text=True
            )

            logs = logs_result.stdout[-1000:] if logs_result.stdout else "No logs available"

            return f"{Colors.CYAN}{info_result.stdout.strip()}{Colors.RESET}\n\n{Colors.YELLOW}Recent Logs:{Colors.RESET}\n{logs}"
        except subprocess.CalledProcessError:
            return f"{Colors.RED}Unable to get info for container: {item['id']}{Colors.RESET}"

    def execute_action(self, item: Dict[str, Any]) -> None:
        if 'Up' in item['status']:
            subprocess.run(['docker', 'exec', '-it', item['id'], '/bin/bash'])
        else:
            subprocess.run(['docker', 'start', '-i', item['id']])

    def get_additional_actions(self) -> Dict[str, str]:
        return {'s': 'Start/Stop container', 'l': 'View logs'}

    def handle_additional_action(self, key: str, item: Dict[str, Any]) -> bool:
        if key == 's':
            try:
                if 'Up' in item['status']:
                    subprocess.run(['docker', 'stop', item['id']], check=True)
                else:
                    subprocess.run(['docker', 'start', item['id']], check=True)
                return True
            except subprocess.CalledProcessError:
                pass
        elif key == 'l':
            subprocess.run(['docker', 'logs', '-f', item['id']])
            return False
        return False


class GhTool(Tool):
    @property
    def name(self) -> str:
        return "gh"

    @property
    def description(self) -> str:
        return "Interactive GitHub pull request picker"

    def is_available(self) -> bool:
        return shutil.which("gh") is not None

    def get_items(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run([
                'gh', 'pr', 'list', '--json',
                'number,title,author,state,url,headRefName,baseRefName,createdAt,updatedAt,additions,deletions,changedFiles'
            ], capture_output=True, text=True, check=True)

            prs = json.loads(result.stdout)
            return prs if prs else []
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def get_item_display(self, item: Dict[str, Any], selected: bool) -> str:
        if selected:
            return f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}🔀 #{item['number']} {item['title'][:50]}{Colors.RESET} {Colors.DIM}by {item['author']['login']}{Colors.RESET}"
        else:
            return f"{Colors.BRIGHT_CYAN}🔀 #{item['number']} {item['title'][:50]}{Colors.RESET} {Colors.DIM}by {item['author']['login']}{Colors.RESET}"

    def get_item_preview(self, item: Dict[str, Any]) -> str:
        try:
            # Get PR commits
            commits_result = subprocess.run([
                'gh', 'pr', 'view', str(item['number']), '--json', 'commits'
            ], capture_output=True, text=True, check=True)

            commits_data = json.loads(commits_result.stdout)
            commits = commits_data.get('commits', [])

            commit_list = []
            for commit in commits[-5:]:
                short_sha = commit['oid'][:8]
                message = commit['messageHeadline'][:50]
                author = commit.get('author', {}).get('name', 'Unknown') if commit.get('author') else 'Unknown'
                commit_list.append(f"{Colors.YELLOW}{short_sha}{Colors.RESET} {message} {Colors.DIM}({author}){Colors.RESET}")

            # Get changed files
            files_result = subprocess.run([
                'gh', 'pr', 'diff', str(item['number']), '--name-only'
            ], capture_output=True, text=True, check=True)

            files = files_result.stdout.strip().split('\n')[:10] if files_result.stdout.strip() else []

            info = f"{Colors.CYAN}PR #{item['number']}: {item['title']}{Colors.RESET}\n"
            info += f"{Colors.DIM}Author: {item['author']['login']} | {item['headRefName']} -> {item['baseRefName']}{Colors.RESET}\n"
            info += f"{Colors.GREEN}+{item.get('additions', 0)} -{item.get('deletions', 0)}{Colors.RESET} changes in {item.get('changedFiles', 0)} files\n\n"

            if commit_list:
                info += f"{Colors.YELLOW}Recent Commits:{Colors.RESET}\n" + '\n'.join(commit_list) + "\n\n"

            if files:
                info += f"{Colors.YELLOW}Changed Files:{Colors.RESET}\n" + '\n'.join(f"{Colors.GREEN}{f}{Colors.RESET}" for f in files)

            return info
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return f"{Colors.RED}Unable to get info for PR #{item['number']}{Colors.RESET}"

    def execute_action(self, item: Dict[str, Any]) -> None:
        webbrowser.open(item['url'])

    def get_additional_actions(self) -> Dict[str, str]:
        return {'c': 'Checkout PR', 'm': 'Merge PR', 'a': 'Create PR'}

    def handle_additional_action(self, key: str, item: Dict[str, Any]) -> bool:
        if key == 'c':
            try:
                subprocess.run(['gh', 'pr', 'checkout', str(item['number'])], check=True)
                return False
            except subprocess.CalledProcessError:
                pass
        elif key == 'm':
            print(f"\n{Colors.YELLOW}Merge PR #{item['number']}? (y/N): {Colors.RESET}", end='', flush=True)
            confirm = sys.stdin.read(1)
            if confirm.lower() == 'y':
                try:
                    subprocess.run(['gh', 'pr', 'merge', str(item['number'])], check=True)
                    return True
                except subprocess.CalledProcessError:
                    pass
        elif key == 'a':
            return self.create_new_item()
        return False

    def can_create_new(self) -> bool:
        return True

    def create_new_item(self) -> bool:
        print(f"\n{Colors.CYAN}Creating new PR...{Colors.RESET}")
        try:
            subprocess.run(['gh', 'pr', 'create'], check=False)
            return True
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}✗ Failed to create PR{Colors.RESET}")
            return False


class CmdPicker:
    def __init__(self, tool: Tool):
        self.tool = tool
        self.items: List[Dict[str, Any]] = []
        self.selected_index: int = 0
        self.preview_height: int = 20

    def get_key(self) -> str:
        """Get a single keypress"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if ord(key) == 27:  # ESC sequence
                key += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def display_interface(self) -> None:
        """Display the picker interface"""
        os.system('clear')

        if not self.items:
            print(f"{Colors.RED}No {self.tool.name} items found{Colors.RESET}")
            return

        # Get terminal size
        try:
            terminal_size = os.get_terminal_size()
            cols = terminal_size.columns
            rows = terminal_size.lines
        except OSError:
            cols, rows = 80, 24

        width = cols

        # Calculate layout
        session_list_height = rows - self.preview_height - 5

        # Header with tool-specific emoji
        tool_emoji = {"tmux": "🚀", "docker": "🐳", "gh": "🔀"}.get(self.tool.name, "🎯")
        print(f"{Colors.BOLD}{Colors.BLUE}{'═' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.WHITE} {tool_emoji} {self.tool.name.upper()} Picker {Colors.RESET}{Colors.DIM}(j/k navigate, Enter select, q quit){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'═' * width}{Colors.RESET}")

        # Display items list
        for i, item in enumerate(self.items):
            if i < session_list_height - 3:  # Leave space for borders
                if i == self.selected_index:
                    marker = f"{Colors.BRIGHT_GREEN}▶ {Colors.RESET}"
                    display = self.tool.get_item_display(item, True)
                else:
                    marker = f"{Colors.DIM}  {Colors.RESET}"
                    display = self.tool.get_item_display(item, False)

                print(f"{marker}{display}")

        # Separator
        print(f"{Colors.YELLOW}{'─' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW} 📋 Item Details & Preview{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─' * width}{Colors.RESET}")

        # Display preview
        if self.items:
            selected_item = self.items[self.selected_index]
            preview = self.tool.get_item_preview(selected_item)
            preview_lines = preview.split('\n')

            # Show preview content
            available_lines = self.preview_height - 3  # Account for headers
            for i, line in enumerate(preview_lines[:available_lines]):
                # Truncate lines to fit terminal width
                truncated_line = line[:width-1] if line else ""
                print(f"{Colors.DIM}{truncated_line}{Colors.RESET}")

        # Display controls at bottom
        controls = ["j/k: Navigate", "Enter: Select", "q: Quit"]
        additional_actions = self.tool.get_additional_actions()
        for key, desc in additional_actions.items():
            controls.append(f"{key}: {desc}")

        print(f"\n{Colors.DIM}Controls: {' | '.join(controls)}{Colors.RESET}")

    def run(self) -> None:
        """Run the picker interface"""
        if not self.tool.is_available():
            print(f"{Colors.RED}Error: {self.tool.name} is not available{Colors.RESET}")
            sys.exit(1)

        self.items = self.tool.get_items()

        if not self.items:
            print(f"{Colors.RED}No {self.tool.name} items found{Colors.RESET}")
            sys.exit(1)

        while True:
            self.display_interface()
            key = self.get_key()

            if key == 'q':
                break
            elif key in ['j', '\x1b[B']:  # j or down arrow
                self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            elif key in ['k', '\x1b[A']:  # k or up arrow
                self.selected_index = max(0, self.selected_index - 1)
            elif key == '\r':  # Enter
                selected_item = self.items[self.selected_index]
                os.system('clear')
                self.tool.execute_action(selected_item)
                break
            else:
                # Check additional actions
                if self.tool.handle_additional_action(key, self.items[self.selected_index]):
                    # Refresh items if action was handled and might have changed state
                    self.items = self.tool.get_items()
                    if not self.items:
                        break
                    self.selected_index = min(self.selected_index, len(self.items) - 1)


TOOLS = {
    'tmux': TmuxTool(),
    'docker': DockerTool(),
    'gh': GhTool(),
}


def main():
    parser = argparse.ArgumentParser(
        description='Unified command picker for various tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available tools:
{chr(10).join(f'  {name}: {tool.description}' for name, tool in TOOLS.items())}

Examples:
  cmd_picker tmux      # Pick tmux sessions
  cmd_picker docker    # Pick docker containers
  cmd_picker gh        # Pick GitHub pull requests
        """
    )

    parser.add_argument('tool', nargs='?', choices=list(TOOLS.keys()),
                       help='Tool to use for picking')

    args = parser.parse_args()

    if not args.tool:
        # Show available tools if no tool specified
        print(f"{Colors.BOLD}🎯 Command Picker{Colors.RESET}")
        print("Available tools:\n")
        for name, tool in TOOLS.items():
            available = "✅" if tool.is_available() else "❌"
            print(f"  {available} {Colors.GREEN}{name}{Colors.RESET}: {tool.description}")
        print("\nUsage: cmd_picker <tool>")
        return

    tool = TOOLS[args.tool]
    picker = CmdPicker(tool)
    picker.run()


if __name__ == "__main__":
    main()
