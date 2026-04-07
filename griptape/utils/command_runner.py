from __future__ import annotations

import shlex
import subprocess

from attrs import define

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact


@define
class CommandRunner:
    """Utility class for running shell commands.

    WARNING: This runner executes commands directly (shell=False) to prevent injection.
    Shell metacharacters (e.g., |, >, &&) are NOT supported and will cause failures.
    """

    def run(self, command: str) -> BaseArtifact:
        try:
            # We use posix=True even on Windows to ensure consistent behavior for shlex.split.
            # subprocess.Popen on Windows handles list arguments correctly by re-encoding them
            # into a command string for CreateProcess.
            args = shlex.split(command, posix=True)
            process = subprocess.Popen(
                args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate()

            if len(stderr) == 0:
                return TextArtifact(stdout.strip().decode("utf-8", errors="replace"))
            return ErrorArtifact(f"error: {stderr.strip().decode('utf-8', errors='replace')}")
        except OSError as e:
            return ErrorArtifact(f"error running command: {e}")
        except Exception as e:
            return ErrorArtifact(f"unexpected error: {e}")
