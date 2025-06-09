import pytest
from unittest.mock import patch, MagicMock
import subprocess

from tmux_picker.tmux_picker import TmuxPicker, Colors, main


class TestTmuxPicker:
    """Test cases for TmuxPicker class"""

    def test_init(self):
        """Test TmuxPicker initialization"""
        picker = TmuxPicker()
        assert picker.sessions == []
        assert picker.selected_index == 0
        assert picker.preview_height == 20

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_tmux_sessions_success(self, mock_run):
        """Test successful retrieval of tmux sessions"""
        mock_result = MagicMock()
        mock_result.stdout = "session1\nsession2\nsession3\n"
        mock_run.return_value = mock_result

        picker = TmuxPicker()
        sessions = picker.get_tmux_sessions()

        assert sessions == ["session1", "session2", "session3"]
        mock_run.assert_called_once_with(
            ['tmux', 'list-sessions', '-F', '#{session_name}'],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_tmux_sessions_empty(self, mock_run):
        """Test retrieval when no tmux sessions exist"""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        picker = TmuxPicker()
        sessions = picker.get_tmux_sessions()

        assert sessions == []

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_tmux_sessions_error(self, mock_run):
        """Test error handling when tmux command fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')

        picker = TmuxPicker()
        sessions = picker.get_tmux_sessions()

        assert sessions == []

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_session_info_success(self, mock_run):
        """Test successful session info retrieval"""
        mock_run.side_effect = [
            MagicMock(stdout="test_session: 3 windows, created Mon Jan 1"),
            MagicMock(stdout="0: bash (active)\n1: vim\n2: htop")
        ]

        picker = TmuxPicker()
        info = picker.get_session_info("test_session")

        expected = f"{Colors.CYAN}test_session: 3 windows, created Mon Jan 1{Colors.RESET}\n\n{Colors.YELLOW}Windows:{Colors.RESET}\n{Colors.GREEN}0: bash (active)\n1: vim\n2: htop{Colors.RESET}"
        assert info == expected

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_session_info_error(self, mock_run):
        """Test error handling for session info retrieval"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')

        picker = TmuxPicker()
        info = picker.get_session_info("nonexistent")

        assert Colors.RED in info
        assert "Unable to get info" in info

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_session_preview_success(self, mock_run):
        """Test successful session preview capture"""
        mock_run.side_effect = [
            MagicMock(stdout="0"),  # active window
            MagicMock(stdout="$ ls\nfile1.txt\nfile2.txt\n$ ")  # pane content
        ]

        picker = TmuxPicker()
        preview = picker.get_session_preview("test_session")

        assert "$ ls" in preview
        assert "file1.txt" in preview

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_get_session_preview_error(self, mock_run):
        """Test error handling for session preview"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')

        picker = TmuxPicker()
        preview = picker.get_session_preview("nonexistent")

        assert Colors.DIM in preview
        assert "No preview available" in preview

    @patch('tmux_picker.tmux_picker.os.system')
    def test_clear_screen(self, mock_system):
        """Test screen clearing"""
        picker = TmuxPicker()
        picker.clear_screen()

        mock_system.assert_called_once_with('clear')

    @patch('tmux_picker.tmux_picker.shutil.get_terminal_size')
    def test_get_terminal_size(self, mock_size):
        """Test terminal size retrieval"""
        mock_size.return_value = MagicMock(lines=50, columns=80)

        picker = TmuxPicker()
        height, width = picker.get_terminal_size()

        assert height == 50
        assert width == 80

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_delete_session_success(self, mock_run):
        """Test successful session deletion"""
        mock_run.return_value = MagicMock()

        picker = TmuxPicker()
        with patch.object(picker, 'clear_screen'), \
             patch.object(picker, 'get_key', return_value='y'), \
             patch('builtins.print'):
            result = picker.delete_session("test_session")

        assert result is True
        mock_run.assert_called_once_with(['tmux', 'kill-session', '-t', 'test_session'], check=True)

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_delete_session_cancelled(self, mock_run):
        """Test cancelled session deletion"""
        picker = TmuxPicker()
        with patch.object(picker, 'clear_screen'), \
             patch.object(picker, 'get_key', return_value='n'), \
             patch('builtins.print'):
            result = picker.delete_session("test_session")

        assert result is False
        mock_run.assert_not_called()

    @patch('tmux_picker.tmux_picker.subprocess.run')
    def test_delete_session_error(self, mock_run):
        """Test session deletion error"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')

        picker = TmuxPicker()
        with patch.object(picker, 'clear_screen'), \
             patch.object(picker, 'get_key', return_value='y'), \
             patch('builtins.print'):
            result = picker.delete_session("test_session")

        assert result is False

    @patch('tmux_picker.tmux_picker.os.execvp')
    def test_attach_to_session_success(self, mock_execvp):
        """Test successful session attachment"""
        picker = TmuxPicker()
        picker.attach_to_session("test_session")

        mock_execvp.assert_called_once_with('tmux', ['tmux', 'attach-session', '-t', 'test_session'])

    @patch('tmux_picker.tmux_picker.os.execvp')
    def test_attach_to_session_error(self, mock_execvp):
        """Test session attachment error"""
        mock_execvp.side_effect = OSError("Command not found")

        picker = TmuxPicker()
        with pytest.raises(SystemExit):
            picker.attach_to_session("test_session")

    @patch('tmux_picker.tmux_picker.shutil.which')
    def test_run_no_tmux(self, mock_which):
        """Test running when tmux is not available"""
        mock_which.return_value = None

        picker = TmuxPicker()
        with pytest.raises(SystemExit):
            picker.run()

    @patch('tmux_picker.tmux_picker.shutil.which')
    @patch.object(TmuxPicker, 'get_tmux_sessions')
    def test_run_no_sessions(self, mock_get_sessions, mock_which):
        """Test running when no tmux sessions exist"""
        mock_which.return_value = '/usr/bin/tmux'
        mock_get_sessions.return_value = []

        picker = TmuxPicker()
        with pytest.raises(SystemExit):
            picker.run()

    @patch('tmux_picker.tmux_picker.shutil.which')
    @patch.object(TmuxPicker, 'get_tmux_sessions')
    @patch.object(TmuxPicker, 'draw_interface')
    @patch.object(TmuxPicker, 'get_key')
    @patch.object(TmuxPicker, 'clear_screen')
    def test_run_quit(self, mock_clear, mock_get_key, mock_draw, mock_get_sessions, mock_which):
        """Test quitting the application"""
        mock_which.return_value = '/usr/bin/tmux'
        mock_get_sessions.return_value = ['session1', 'session2']
        mock_get_key.return_value = 'q'

        picker = TmuxPicker()
        picker.run()

        mock_draw.assert_called()
        mock_clear.assert_called()

    @patch('tmux_picker.tmux_picker.shutil.which')
    @patch.object(TmuxPicker, 'get_tmux_sessions')
    @patch.object(TmuxPicker, 'draw_interface')
    @patch.object(TmuxPicker, 'get_key')
    @patch.object(TmuxPicker, 'clear_screen')
    def test_run_navigation(self, mock_clear, mock_get_key, mock_draw, mock_get_sessions, mock_which):
        """Test navigation keys"""
        mock_which.return_value = '/usr/bin/tmux'
        mock_get_sessions.return_value = ['session1', 'session2', 'session3']
        mock_get_key.side_effect = ['j', 'k', 'q']  # down, up, quit

        picker = TmuxPicker()
        picker.run()

        # Should have moved selection down then up
        assert picker.selected_index == 0  # back to starting position

    @patch('tmux_picker.tmux_picker.shutil.which')
    @patch.object(TmuxPicker, 'get_tmux_sessions')
    @patch.object(TmuxPicker, 'draw_interface')
    @patch.object(TmuxPicker, 'get_key')
    @patch.object(TmuxPicker, 'delete_session')
    @patch.object(TmuxPicker, 'clear_screen')
    def test_run_delete_session(self, mock_clear, mock_delete, mock_get_key, mock_draw, mock_get_sessions, mock_which):
        """Test deleting a session"""
        mock_which.return_value = '/usr/bin/tmux'
        mock_get_sessions.side_effect = [['session1', 'session2'], ['session1']]  # before and after deletion
        mock_get_key.side_effect = ['d', 'q']  # delete, quit
        mock_delete.return_value = True

        picker = TmuxPicker()
        picker.run()

        mock_delete.assert_called_once_with('session1')

    @patch('tmux_picker.tmux_picker.shutil.which')
    @patch.object(TmuxPicker, 'get_tmux_sessions')
    @patch.object(TmuxPicker, 'draw_interface')
    @patch.object(TmuxPicker, 'get_key')
    @patch.object(TmuxPicker, 'attach_to_session')
    @patch.object(TmuxPicker, 'clear_screen')
    def test_run_attach_session(self, mock_clear, mock_attach, mock_get_key, mock_draw, mock_get_sessions, mock_which):
        """Test attaching to a session"""
        mock_which.return_value = '/usr/bin/tmux'
        mock_get_sessions.return_value = ['session1', 'session2']
        mock_get_key.return_value = '\r'  # Enter key

        picker = TmuxPicker()
        picker.run()

        mock_attach.assert_called_once_with('session1')


class TestColors:
    """Test the Colors class constants"""

    def test_colors_exist(self):
        """Test that all color constants are defined"""
        assert hasattr(Colors, 'RESET')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'MAGENTA')


@patch.object(TmuxPicker, 'run')
def test_main(mock_run):
    """Test the main function"""
    main()
    mock_run.assert_called_once()


@pytest.mark.parametrize("test_case", [
    ("session1", "session1"),
    ("my-session", "my-session"),
    ("session_with_underscores", "session_with_underscores"),
])
def test_session_name_handling(test_case):
    """Test handling of various session name formats"""
    input_session, expected = test_case
    picker = TmuxPicker()

    with patch.object(picker, 'clear_screen'), \
         patch.object(picker, 'get_key', return_value='n'), \
         patch('builtins.print'):
        result = picker.delete_session(input_session)

    assert result is False  # Should be cancelled, but function should handle the name correctly
