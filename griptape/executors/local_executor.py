from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import os
import subprocess
from attr import define, field
from griptape.executors import BaseExecutor

if TYPE_CHECKING:
    from griptape.core import BaseTool


@define
class LocalExecutor(BaseExecutor):
    verbose: int = field(default=False, kw_only=True)

    def try_execute(self, tool_activity: callable, value: bytes) -> bytes:
        tool = tool_activity.__self__

        logging.warning(f"You are executing the {tool.name} tool in the local environment. Make sure to "
                        f"switch to a more secure ToolExecutor in production.")

        env = os.environ.copy()

        env.update(tool.env)

        self.install_dependencies(env, tool)

        output = self.run_subprocess(env, tool_activity, value)

        if output.stderr:
            return output.stderr.strip().encode()
        else:
            return output.stdout.strip().encode()

    def install_dependencies(self, env: dict[str, str], tool: BaseTool) -> None:
        command = [
            "pip",
            "install",
            "--trusted-host",
            "pypi.python.org",
            "-r",
            "requirements.txt"
        ]

        subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL
        )

    def run_subprocess(self, env: dict[str, str], tool_activity: callable, value: bytes) -> subprocess.CompletedProcess:
        tool = tool_activity.__self__
        tool_name = tool.class_name
        command = [
            "python",
            "-c",
            f'from tool import {tool_name}; print({tool_name}().{tool_activity.__name__}({value}))'
        ]

        return subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            capture_output=True,
            text=True
        )
