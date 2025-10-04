#!/usr/bin/env python3

import pytest
from unittest.mock import Mock, patch
import subprocess

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from py_scripts.cmd_picker.cmd_picker import TmuxTool, DockerTool, GhTool, CmdPicker


class TestTmuxTool:
    def test_name_and_description(self):
        tool = TmuxTool()
        assert tool.name == "tmux"
        assert "tmux session" in tool.description.lower()

    @patch("shutil.which")
    def test_is_available(self, mock_which):
        tool = TmuxTool()
        mock_which.return_value = "/usr/bin/tmux"
        assert tool.is_available()

        mock_which.return_value = None
        assert not tool.is_available()

    @patch("subprocess.run")
    def test_get_items_success(self, mock_run):
        tool = TmuxTool()
        mock_run.return_value = Mock(stdout="session1\t3\t1234567890\nsession2\t1\t1234567891\n", returncode=0)

        items = tool.get_items()

        assert len(items) == 2
        assert items[0]["name"] == "session1"
        assert items[0]["windows"] == "3"
        assert items[1]["name"] == "session2"
        assert items[1]["windows"] == "1"

    @patch("subprocess.run")
    def test_get_items_failure(self, mock_run):
        tool = TmuxTool()
        mock_run.side_effect = subprocess.CalledProcessError(1, "tmux")

        items = tool.get_items()
        assert items == []

    def test_get_item_display(self):
        tool = TmuxTool()
        item = {"name": "test_session", "windows": "2", "created": "1234567890"}

        # Test selected
        display = tool.get_item_display(item, selected=True)
        assert "test_session" in display
        assert "2 windows" in display

        # Test not selected
        display = tool.get_item_display(item, selected=False)
        assert "test_session" in display


class TestDockerTool:
    def test_name_and_description(self):
        tool = DockerTool()
        assert tool.name == "docker"
        assert "docker container" in tool.description.lower()

    @patch("shutil.which")
    def test_is_available(self, mock_which):
        tool = DockerTool()
        mock_which.return_value = "/usr/bin/docker"
        assert tool.is_available()

        mock_which.return_value = None
        assert not tool.is_available()

    @patch("subprocess.run")
    def test_get_items_success(self, mock_run):
        tool = DockerTool()
        mock_run.return_value = Mock(stdout="abc123456789\ttest_container\tUp 2 hours\tnginx:latest\n", returncode=0)

        items = tool.get_items()

        assert len(items) == 1
        assert items[0]["id"] == "abc123456789"
        assert items[0]["name"] == "test_container"
        assert items[0]["status"] == "Up 2 hours"
        assert items[0]["image"] == "nginx:latest"

    def test_get_item_display(self):
        tool = DockerTool()
        item = {"id": "abc123456789", "name": "test_container", "status": "Up 2 hours", "image": "nginx:latest"}

        display = tool.get_item_display(item, selected=True)
        assert "test_container" in display
        assert "abc123456789" in display
        assert "Up 2 hours" in display


class TestGhTool:
    def test_name_and_description(self):
        tool = GhTool()
        assert tool.name == "gh"
        assert "github" in tool.description.lower() or "pull request" in tool.description.lower()

    @patch("shutil.which")
    def test_is_available(self, mock_which):
        tool = GhTool()
        mock_which.return_value = "/usr/bin/gh"
        assert tool.is_available()

        mock_which.return_value = None
        assert not tool.is_available()

    @patch("subprocess.run")
    def test_get_items_success(self, mock_run):
        tool = GhTool()
        mock_run.return_value = Mock(
            stdout='[{"number": 123, "title": "Test PR", "author": {"login": "testuser"}, "state": "open", "url": "https://github.com/test/repo/pull/123"}]',
            returncode=0,
        )

        items = tool.get_items()

        assert len(items) == 1
        assert items[0]["number"] == 123
        assert items[0]["title"] == "Test PR"
        assert items[0]["author"]["login"] == "testuser"

    @patch("subprocess.run")
    def test_get_items_failure(self, mock_run):
        tool = GhTool()
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh")

        items = tool.get_items()
        assert items == []

    def test_get_item_display(self):
        tool = GhTool()
        item = {"number": 123, "title": "Test pull request title", "author": {"login": "testuser"}}

        display = tool.get_item_display(item, selected=True)
        assert "#123" in display
        assert "Test pull request title" in display
        assert "testuser" in display


class TestCmdPicker:
    @patch.object(TmuxTool, "is_available", return_value=True)
    @patch.object(
        TmuxTool,
        "get_items",
        return_value=[{"name": "session1", "windows": "2", "created": "1234567890", "type": "session"}],
    )
    def test_initialization(self, mock_get_items, mock_is_available):
        tool = TmuxTool()
        picker = CmdPicker(tool)

        assert picker.tool == tool
        assert picker.selected_index == 0
        assert picker.preview_height == 20

    @patch.object(TmuxTool, "is_available", return_value=False)
    def test_run_tool_not_available(self, mock_is_available):
        tool = TmuxTool()
        picker = CmdPicker(tool)

        with pytest.raises(SystemExit):
            picker.run()

    @patch.object(TmuxTool, "is_available", return_value=True)
    @patch.object(TmuxTool, "get_items", return_value=[])
    def test_run_no_items(self, mock_get_items, mock_is_available):
        tool = TmuxTool()
        picker = CmdPicker(tool)

        with pytest.raises(SystemExit):
            picker.run()


if __name__ == "__main__":
    pytest.main([__file__])
