from __future__ import annotations
import logging
import subprocess
import sys
from functools import reduce
from typing import TYPE_CHECKING, Union
import inspect
import os
from abc import ABC
from typing import Optional
import yaml
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, InfoArtifact, TextArtifact
from griptape.mixins import ActivityMixin

if TYPE_CHECKING:
    from griptape.memory.tool import BaseToolMemory
    from griptape.tasks import ActionSubtask


@define
class BaseTool(ActivityMixin, ABC):
    MANIFEST_FILE = "manifest.yml"
    REQUIREMENTS_FILE = "requirements.txt"

    name: str = field(default=Factory(lambda self: self.class_name, takes_self=True), kw_only=True)
    input_memory: Optional[list[BaseToolMemory]] = field(default=None, kw_only=True)
    output_memory: Optional[dict[str, list[BaseToolMemory]]] = field(default=None, kw_only=True)
    install_dependencies_on_init: bool = field(default=True, kw_only=True)
    dependencies_install_directory: Optional[str] = field(default=None, kw_only=True)
    verbose: bool = field(default=False, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.install_dependencies_on_init:
            self.install_dependencies(os.environ.copy())

    @output_memory.validator
    def validate_output_memory(self, _, output_memory: Optional[dict[str, list[BaseToolMemory]]]) -> None:
        if output_memory:
            for activity_name, memory_list in output_memory.items():
                if not self.find_activity(activity_name):
                    raise ValueError(f"activity {activity_name} doesn't exist")

                output_memory_names = [memory.name for memory in memory_list]

                if len(output_memory_names) > len(set(output_memory_names)):
                    raise ValueError(f"memory names have to be unique in activity '{activity_name}' output")

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def manifest_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.MANIFEST_FILE)

    @property
    def requirements_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.REQUIREMENTS_FILE)

    @property
    def manifest(self) -> dict:
        with open(self.manifest_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)

    @property
    def abs_file_path(self):
        return os.path.abspath(inspect.getfile(self.__class__))

    @property
    def abs_dir_path(self):
        return os.path.dirname(self.abs_file_path)

    def before_execute(self, activity: callable, value: Optional[dict]) -> Optional[dict]:
        return value

    def execute(self, activity: callable, subtask: ActionSubtask) -> BaseArtifact:
        preprocessed_value = self.before_execute(activity, subtask.action_input)

        activity_result = activity(preprocessed_value)

        if isinstance(activity_result, BaseArtifact):
            result = activity_result
        else:
            logging.warning("Activity result is not an artifact; converting result to InfoArtifact")

            result = InfoArtifact(activity_result)

        return self.after_execute(activity, subtask, result)

    def after_execute(self, activity: callable, subtask: ActionSubtask, value: BaseArtifact) -> BaseArtifact:
        if self.output_memory:
            for memory in activity.__self__.output_memory.get(activity.name, []):
                value = memory.process_output(activity, subtask, value)

            if isinstance(value, BaseArtifact):
                return value
            else:
                return TextArtifact(str(value))
        else:
            return value

    def validate(self) -> bool:
        from griptape.utils import ManifestValidator

        if not os.path.exists(self.manifest_path):
            raise Exception(f"{self.MANIFEST_FILE} not found")

        if not os.path.exists(self.requirements_path):
            raise Exception(f"{self.REQUIREMENTS_FILE} not found")

        ManifestValidator().validate(self.manifest)

        return True

    def tool_dir(self):
        class_file = inspect.getfile(self.__class__)

        return os.path.dirname(os.path.abspath(class_file))

    def install_dependencies(self, env: Optional[dict[str, str]] = None) -> None:
        env = env if env else {}

        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ]

        if self.dependencies_install_directory is None:
            command.extend(["-U"])
        else:
            command.extend(["-t", self.dependencies_install_directory])

        subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(),
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL
        )

    def find_input_memory(self, memory_name: str) -> Optional[BaseToolMemory]:
        if self.input_memory:
            return next((m for m in self.input_memory if m.name == memory_name), None)
        else:
            return None
