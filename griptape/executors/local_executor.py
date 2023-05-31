from __future__ import annotations
import logging
import os
import subprocess
from typing import TYPE_CHECKING, Union, Optional
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.executors import BaseExecutor

if TYPE_CHECKING:
    from griptape.core import BaseTool


@define
class LocalExecutor(BaseExecutor):
    verbose: int = field(default=False, kw_only=True)

    dependencies_install_directory = field(default=None, kw_only=True)

    def try_execute(self, tool_activity: callable, value: Optional[dict]) -> Union[BaseArtifact, str]:
        tool = tool_activity.__self__

        logging.warning(f"You are executing the {tool.name} tool in the local environment. Make sure to "
                        f"switch to a more secure ToolExecutor in production.")

        env = os.environ.copy()

        env.update(tool.env)

        output = self.run_subprocess(env, tool_activity, value)

        if output.stderr and not output.stdout:
            return ErrorArtifact(output.stderr.strip())
        else:
            return output.stdout.strip()

    def install_dependencies(self, env: dict[str, str], tool: BaseTool) -> None:
        if self.dependencies_install_directory is None:
            command = [
                "pip",
                "install",
                "-r",
                "requirements.txt",
                "-U"
            ]
        else:
            command = [
                "pip",
                "install",
                "-r",
                "requirements.txt",
                "-t",
                self.dependencies_install_directory
            ]

        subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL
        )

    def run_subprocess(
            self,
            env: dict[str, str],
            tool_activity: callable,
            value: Optional[dict]
    ) -> subprocess.CompletedProcess:
        tool = tool_activity.__self__
        tool_name = tool.class_name
        input_value = value if value else ""
        code = []

        if self.dependencies_install_directory is not None:
            code.extend([
                'from sys import path',
                f'path.insert(1, "{self.dependencies_install_directory}")'
            ])

        code.extend([
            f'from tool import {tool_name}',
            f'print({tool_name}().{tool_activity.__name__}({input_value}))'
        ])

        code = str.join(';', code)

        command = [
            "python",
            "-c",
            code
        ]

        return subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(tool),
            capture_output=True,
            text=True
        )
