from __future__ import annotations

import os
import sys

import pytest

from griptape.artifacts import ErrorArtifact
from griptape.utils import CommandRunner


class TestCommandRunner:
    def test_run(self):
        assert "test" in CommandRunner().run(f'"{sys.executable}" -c "print(\'test\')"').value

    def test_run_with_arguments(self):
        # Test command with multiple arguments
        result = CommandRunner().run(f'"{sys.executable}" -c "import sys; print(\' \'.join(sys.argv[1:]))" hello world')
        assert "hello world" in result.value

    def test_shell_metacharacters_ignored(self):
        # In shell=False mode, pipes should not work and be treated as literal arguments to the first command
        # We use a python script that prints all its arguments to verify
        result = CommandRunner().run(
            f'"{sys.executable}" -c "import sys; print(\' \'.join(sys.argv[1:]))" test | echo polluted'
        )
        assert "test" in result.value
        assert "polluted" in result.value
        assert "|" in result.value
        # If shell=True worked, the output would be just 'polluted' (from the second echo)
        assert result.value.strip() != "polluted"

    def test_command_not_found(self):
        # Non-existent command should return an ErrorArtifact
        result = CommandRunner().run("non_existent_command_12345")
        assert isinstance(result, ErrorArtifact)
        # Windows error message: "The system cannot find the file specified"
        # POSIX error message: "No such file or directory"
        value = result.value.lower()
        assert any(msg in value for msg in ["no such file", "not found", "cannot find the file"])

    @pytest.mark.skipif(os.name != "nt", reason="Windows specific test")
    def test_windows_paths(self):
        # Ensure backslashes are handled correctly on Windows
        path = "C:\\Users\\Test"
        # Use quotes so shlex.split handles it correctly on all platforms
        result = CommandRunner().run(f'"{sys.executable}" -c "import sys; print(sys.argv[1])" "{path}"')
        assert path in result.value

    @pytest.mark.skipif(os.name == "nt", reason="POSIX specific test")
    def test_posix_shlex(self):
        # Ensure shlex correctly handles complex POSIX strings
        result = CommandRunner().run(f'"{sys.executable}" -c "import sys; print(sys.argv[1])" "quoted \'string\'"')
        assert "quoted 'string'" in result.value
