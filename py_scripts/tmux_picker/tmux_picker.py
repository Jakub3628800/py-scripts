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
from typing import List, Tuple


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


class TmuxPicker:
    def __init__(self) -> None:
        self.sessions: List[str] = []
        self.selected_index: int = 0
        self.preview_height: int = 20

    def get_tmux_sessions(self) -> List[str]:
        """Get list of tmux sessions"""
        try:
            result = subprocess.run(
                ['tmux', 'list-sessions', '-F', '#{session_name}'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []

    def get_session_info(self, session_name: str) -> str:
        """Get detailed info about a specific session"""
        try:
            # Get session info
            session_info = subprocess.run(
                ['tmux', 'display-message', '-t', session_name, '-p',
                 '#{session_name}: #{session_windows} windows, created #{session_created}'],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            # Get window list
            windows = subprocess.run(
                ['tmux', 'list-windows', '-t', session_name, '-F',
                 '#{window_index}: #{window_name} #{?window_active,(active),}'],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            return f"{Colors.CYAN}{session_info}{Colors.RESET}\n\n{Colors.YELLOW}Windows:{Colors.RESET}\n{Colors.GREEN}{windows}{Colors.RESET}"
        except subprocess.CalledProcessError:
            return f"{Colors.RED}Unable to get info for session: {session_name}{Colors.RESET}"

    def get_session_preview(self, session_name: str) -> str:
        """Get actual tmux session content preview"""
        try:
            # Get the active window for the session
            active_window = subprocess.run(
                ['tmux', 'display-message', '-t', session_name, '-p', '#{window_index}'],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            # Capture the current pane content
            pane_content = subprocess.run(
                ['tmux', 'capture-pane', '-t', f'{session_name}:{active_window}', '-p'],
                capture_output=True,
                text=True,
                check=True
            ).stdout

            return pane_content
        except subprocess.CalledProcessError:
            return f"{Colors.DIM}No preview available{Colors.RESET}"

    def clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('clear')

    def get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal dimensions"""
        size = shutil.get_terminal_size()
        return size.lines, size.columns

    def draw_interface(self) -> None:
        """Draw the main interface"""
        self.clear_screen()
        height, width = self.get_terminal_size()

        # Calculate layout
        session_list_height = height - self.preview_height - 5

        # Header
        print(f"{Colors.BOLD}{Colors.BLUE}{'═' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.WHITE} 🚀 TMUX Session Picker {Colors.RESET}{Colors.DIM}(j/k navigate, Enter attach, d delete, q quit){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'═' * width}{Colors.RESET}")

        # Draw session list
        for i, session in enumerate(self.sessions):
            if i < session_list_height - 3:  # Leave space for borders
                if i == self.selected_index:
                    marker = f"{Colors.BRIGHT_GREEN}▶ {Colors.RESET}"
                    session_color = f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}"
                    reset = Colors.RESET
                else:
                    marker = f"{Colors.DIM}  {Colors.RESET}"
                    session_color = f"{Colors.BRIGHT_CYAN}"
                    reset = Colors.RESET

                print(f"{marker}{session_color}{session}{reset}")

        # Separator
        print(f"{Colors.YELLOW}{'─' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW} 📋 Session Info & Live Preview{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─' * width}{Colors.RESET}")

        # Draw preview
        if self.sessions and self.selected_index < len(self.sessions):
            selected_session = self.sessions[self.selected_index]

            # Show session info first (3 lines)
            info = self.get_session_info(selected_session)
            info_lines = info.split('\n')
            for line in info_lines[:3]:
                print(line[:width-1])

            # Show actual session content
            print(f"{Colors.MAGENTA}{'─' * width}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA} 📺 Live Session Content{Colors.RESET}")
            print(f"{Colors.MAGENTA}{'─' * width}{Colors.RESET}")

            preview = self.get_session_preview(selected_session)
            preview_lines = preview.split('\n')

            # Show last N lines of the session (most recent content)
            available_lines = self.preview_height - 6  # Account for headers and info
            start_idx = max(0, len(preview_lines) - available_lines)

            for line in preview_lines[start_idx:start_idx + available_lines]:
                # Truncate and add subtle dimming to preview content
                truncated_line = line[:width-1] if line else ""
                print(f"{Colors.DIM}{truncated_line}{Colors.RESET}")

    def get_key(self) -> str:
        """Get a single keypress from user"""
        fd: int = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key: str = sys.stdin.read(1)

            # Handle arrow keys (they send escape sequences)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                if key == '\x1b[A':  # Up arrow
                    return 'up'
                elif key == '\x1b[B':  # Down arrow
                    return 'down'

            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def delete_session(self, session_name: str) -> bool:
        """Delete a tmux session with confirmation"""
        self.clear_screen()
        print(f"{Colors.RED}🗑️  Delete session '{Colors.BOLD}{session_name}{Colors.RESET}{Colors.RED}'?{Colors.RESET}")
        print(f"{Colors.YELLOW}This action cannot be undone!{Colors.RESET}")
        print(f"{Colors.DIM}Press Y to confirm, N to cancel{Colors.RESET}")

        while True:
            key: str = self.get_key()
            if key.lower() == 'y':
                try:
                    subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True)
                    print(f"{Colors.GREEN}✓ Session '{session_name}' deleted{Colors.RESET}")
                    return True
                except subprocess.CalledProcessError:
                    print(f"{Colors.RED}✗ Failed to delete session '{session_name}'{Colors.RESET}")
                    return False
            elif key.lower() == 'n' or key == '\x1b':  # N or ESC
                return False

    def attach_to_session(self, session_name: str) -> None:
        """Attach to the selected tmux session"""
        try:
            os.execvp('tmux', ['tmux', 'attach-session', '-t', session_name])
        except OSError as e:
            print(f"Error attaching to session: {e}")
            sys.exit(1)

    def run(self) -> None:
        """Main application loop"""
        # Check if tmux is available
        if not shutil.which('tmux'):
            print("Error: tmux is not installed or not in PATH")
            sys.exit(1)

        # Get sessions
        self.sessions = self.get_tmux_sessions()

        if not self.sessions:
            print(f"{Colors.YELLOW}⚠️  No tmux sessions found.{Colors.RESET}")
            print(f"{Colors.CYAN}💡 Create a new session with: {Colors.BOLD}tmux new-session -d -s <session_name>{Colors.RESET}")
            sys.exit(0)

        try:
            while True:
                self.draw_interface()

                key: str = self.get_key()

                if key == 'q' or key == '\x03':  # q or Ctrl+C
                    break
                elif (key == 'k' or key == 'up') and self.selected_index > 0:
                    self.selected_index -= 1
                elif (key == 'j' or key == 'down') and self.selected_index < len(self.sessions) - 1:
                    self.selected_index += 1
                elif key == 'd':  # Delete session
                    session_to_delete: str = self.sessions[self.selected_index]
                    if self.delete_session(session_to_delete):
                        # Refresh session list after deletion
                        self.sessions = self.get_tmux_sessions()
                        if not self.sessions:
                            print(f"{Colors.YELLOW}⚠️  No tmux sessions remaining.{Colors.RESET}")
                            break
                        # Adjust selected index if needed
                        if self.selected_index >= len(self.sessions):
                            self.selected_index = len(self.sessions) - 1
                elif key == '\r' or key == '\n':  # Enter
                    session_to_attach: str = self.sessions[self.selected_index]
                    self.clear_screen()
                    print(f"{Colors.GREEN}🔗 Attaching to session: {Colors.BOLD}{session_to_attach}{Colors.RESET}")
                    self.attach_to_session(session_to_attach)
                    break

        except KeyboardInterrupt:
            pass
        finally:
            self.clear_screen()


def main() -> None:
    picker: TmuxPicker = TmuxPicker()
    picker.run()


if __name__ == "__main__":
    main()
