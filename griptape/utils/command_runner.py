from __future__ import annotations

import os
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
            # Detect the OS and set posix mode accordingly so Windows paths don't break.
            args = shlex.split(command, posix=(os.name == "posix"))
            process = subprocess.Popen(
                args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate()

            if len(stderr) == 0:
                return TextArtifact(stdout.strip().decode("utf-8"))
            return ErrorArtifact(f"error: {stderr.strip().decode('utf-8')}")
        except OSError as e:
            return ErrorArtifact(f"error running command: {e}")
