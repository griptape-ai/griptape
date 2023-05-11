from __future__ import annotations
import logging
import os
import subprocess
from typing import TYPE_CHECKING, Union, Optional
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.executors import BaseExecutor



if TYPE_CHECKING:
    from griptape.core import BaseTool


@define
class LambdaExecutor(BaseExecutor):
    verbose: bool = field(default=False, kw_only=True)
    install_dependencies: bool = field(default=True, kw_only=True)

    def try_execute(self, tool_activity: callable, value: Optional[dict]) -> Union[BaseArtifact, str]:
        tool = tool_activity.__self__

        env = os.environ.copy()

        env.update(tool.env)

        if self.install_dependencies:
            self.install_dependencies(env, tool)

        output = self.run_subprocess(env, tool_activity, value)

        if output.stderr and not output.stdout:
            return ErrorArtifact(output.stderr.strip())
        else:
            return output.stdout.strip()

    def install_dependencies(self, env: dict[str, str], tool: BaseTool) -> None:
        command = [
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "-t",
            f'/tmp/deps/{tool.class_name}/',
            "--no-cache-dir"
        ]
        print(command)

        subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL
        )

    def run_subprocess(self, env: dict[str, str], tool_activity: callable, value: Optional[dict]) -> subprocess.CompletedProcess:
        tool = tool_activity.__self__
        tool_name = tool.class_name
        input_value = value if value else ""
        deps_dir = f'/tmp/deps/{tool_name}/' if self.install_dependencies else '/var/task/'

        command = [
            "python",
            "-c",
            f'from sys import path; path.insert(1, "{deps_dir}"); from tool import {tool_name}; print({tool_name}().{tool_activity.__name__}({input_value}))'
        ]

        return subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            capture_output=True,
            text=True
        )
