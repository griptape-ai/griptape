from __future__ import annotations
import json
import logging
import subprocess
import sys
from typing import TYPE_CHECKING
import inspect
import os
from abc import ABC
from typing import Optional
import yaml
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.core import ActivityMixin

if TYPE_CHECKING:
    from griptape.memory.tool import BaseToolMemory


@define
class BaseTool(ActivityMixin, ABC):
    MANIFEST_FILE = "manifest.yml"
    REQUIREMENTS_FILE = "requirements.txt"

    name: str = field(default=Factory(lambda self: self.class_name, takes_self=True), kw_only=True)
    memory: dict[str, dict[str, list[BaseToolMemory]]] = field(factory=dict, kw_only=True)
    install_dependencies_on_init: bool = field(default=True, kw_only=True)
    dependencies_install_directory: Optional[str] = field(default=None, kw_only=True)
    verbose: bool = field(default=False, kw_only=True)
    artifacts: list[BaseArtifact] = field(factory=list, kw_only=True)

    def __attrs_post_init__(self):
        if self.install_dependencies_on_init:
            self.install_dependencies(os.environ.copy())

    @memory.validator
    def validate_memory(self, _, memory: dict[str, dict[str, list[BaseToolMemory]]]) -> None:
        for activity_name, memory_dict in memory.items():
            if not self.find_activity(activity_name):
                raise ValueError(f"activity {activity_name} doesn't exist")

            input_memory_names = [memory.name for memory in memory_dict.get("input", [])]

            if len(input_memory_names) > len(set(input_memory_names)):
                raise ValueError(f"memory names have to be unique in activity '{activity_name}' input")

            output_memory_names = [memory.name for memory in memory_dict.get("output", [])]

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
        for memory in activity.__self__.memory.get(activity.name, {}).get("input", []):
            value = memory.process_input(activity, value)

        return value

    def execute(self, activity: callable, value: Optional[dict]) -> BaseArtifact:
        preprocessed_value = self.before_execute(activity, value)

        activity_result = activity(preprocessed_value)

        if isinstance(activity_result, BaseArtifact):
            result_artifact = activity_result
        else:
            try:
                result_artifact = BaseArtifact.from_dict(json.loads(activity_result))
            except Exception:
                logging.error("Error converting tool activity result to an artifact; defaulting to InfoArtifact")

                result_artifact = InfoArtifact(activity_result)

        return self.after_execute(activity, result_artifact)

    def after_execute(self, activity: callable, value: Optional[BaseArtifact]) -> BaseArtifact:
        for memory in activity.__self__.memory.get(activity.name, {}).get("output", []):
            value = memory.process_output(activity, value)

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
