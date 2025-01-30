from __future__ import annotations

import importlib.metadata
import inspect
import logging
import os
import re
import subprocess
import sys
import traceback
from abc import ABC
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

import schema
from attrs import Attribute, Factory, define, field
from schema import Literal, Or, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact
from griptape.common import observable
from griptape.configs import Defaults
from griptape.mixins.activity_mixin import ActivityMixin
from griptape.mixins.runnable_mixin import RunnableMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.common import ToolAction
    from griptape.memory import TaskMemory
    from griptape.tasks import ActionsSubtask


logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseTool(ActivityMixin, SerializableMixin, RunnableMixin["BaseTool"], ABC):
    """Abstract class for all tools to inherit from for.

    Attributes:
        name: Tool name.
        input_memory: TaskMemory available in tool activities. Gets automatically set if None.
        output_memory: TaskMemory that activities write to be default. Gets automatically set if None.
        install_dependencies_on_init: Determines whether dependencies from the tool requirements.txt file are installed in init.
        dependencies_install_directory: Custom dependency install directory.
        verbose: Determines whether tool operations (such as dependency installation) should be verbose.
        off_prompt: Determines whether tool activity output goes to the output memory.
    """

    REQUIREMENTS_FILE = "requirements.txt"

    name: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    input_memory: Optional[list[TaskMemory]] = field(default=None, kw_only=True, metadata={"serializable": True})
    output_memory: Optional[dict[str, list[TaskMemory]]] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    install_dependencies_on_init: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    dependencies_install_directory: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    verbose: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    off_prompt: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        if (
            self.install_dependencies_on_init
            and self.has_requirements
            and not self.are_requirements_met(self.requirements_path)
        ):
            self.install_dependencies(os.environ.copy())

    @output_memory.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_output_memory(self, _: Attribute, output_memory: dict[str, Optional[list[TaskMemory]]]) -> None:
        if output_memory:
            for activity_name, memory_list in output_memory.items():
                if not self.find_activity(activity_name):
                    raise ValueError(f"activity {activity_name} doesn't exist")
                if memory_list is None:
                    raise ValueError(f"memory list for activity '{activity_name}' can't be None")

                output_memory_names = [memory.name for memory in memory_list]

                if len(output_memory_names) > len(set(output_memory_names)):
                    raise ValueError(f"memory names have to be unique in activity '{activity_name}' output")

    @property
    def requirements_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.REQUIREMENTS_FILE)

    @property
    def abs_file_path(self) -> str:
        return os.path.abspath(inspect.getfile(self.__class__))

    @property
    def abs_dir_path(self) -> str:
        return os.path.dirname(self.abs_file_path)

    @property
    def has_requirements(self) -> bool:
        return os.path.exists(self.requirements_path)

    # This method has to remain a method and can't be decorated with @property because
    # of the max depth recursion issue in `self.activities`.
    def schema(self) -> dict:
        full_schema = Schema(Or(*self.activity_schemas()), description=f"{self.name} action schema.")

        return full_schema.json_schema(f"{self.name} ToolAction Schema")

    def activity_schemas(self) -> list[Schema]:
        schemas = []

        for activity in self.activities():
            schema_dict: dict[Literal | schema.Optional, Any] = {
                Literal("name"): self.name,
                Literal("path", description=self.activity_description(activity)): self.activity_name(activity),
            }

            activity_schema = self.activity_schema(activity)
            # If no schema is defined, we just make `input` optional instead of omitting it.
            # This works better with lower-end models that may accidentally pass in an empty dict.
            if activity_schema is None:
                schema_dict[schema.Optional("input")] = {}
            else:
                schema_dict[Literal("input")] = activity_schema.schema

            schemas.append(Schema(schema_dict))

        return schemas

    def run(self, activity: Callable, subtask: ActionsSubtask, action: ToolAction) -> BaseArtifact:
        try:
            output = self.before_run(activity, subtask, action)

            output = self.try_run(activity, subtask, action, output)

            output = self.after_run(activity, subtask, action, output)
        except Exception as e:
            logging.debug(traceback.format_exc())
            output = ErrorArtifact(str(e), exception=e)

        return output

    def before_run(self, activity: Callable, subtask: ActionsSubtask, action: ToolAction) -> Optional[dict]:
        super().before_run()

        return action.input

    @observable(tags=["Tool.run()"])
    def try_run(
        self,
        activity: Callable,
        subtask: ActionsSubtask,
        action: ToolAction,
        value: Optional[dict],
    ) -> BaseArtifact:
        activity_result = activity(deepcopy(value))

        if isinstance(activity_result, BaseArtifact):
            result = activity_result
        else:
            logging.warning("Activity result is not an artifact; converting result to InfoArtifact")

            if activity_result is None:
                result = InfoArtifact("Tool returned an empty value")
            else:
                result = InfoArtifact(activity_result)

        return result

    def after_run(
        self,
        activity: Callable,
        subtask: ActionsSubtask,
        action: ToolAction,
        value: BaseArtifact,
    ) -> BaseArtifact:
        super().after_run()

        if self.output_memory:
            output_memories = self.output_memory[getattr(activity, "name")] or []
            for memory in output_memories:
                value = memory.process_output(activity, subtask, value)

            return value
        else:
            return value

    def validate(self) -> bool:
        if not os.path.exists(self.requirements_path):
            raise Exception(f"{self.REQUIREMENTS_FILE} not found")
        return True

    def tool_dir(self) -> str:
        class_file = inspect.getfile(self.__class__)

        return os.path.dirname(os.path.abspath(class_file))

    def install_dependencies(self, env: Optional[dict[str, str]] = None) -> None:
        env = env or {}

        command = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

        if self.dependencies_install_directory is None:
            command.extend(["-U"])
        else:
            command.extend(["-t", self.dependencies_install_directory])

        subprocess.run(
            command,
            env=env,
            cwd=self.tool_dir(),
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL,
        )

    def find_input_memory(self, memory_name: str) -> Optional[TaskMemory]:
        if self.input_memory:
            return next((m for m in self.input_memory if m.name == memory_name), None)
        else:
            return None

    def to_native_tool_name(self, activity: Callable) -> str:
        """Converts a Tool's name and an Activity into to a native tool name.

        The native tool name is a combination of the Tool's name and the Activity's name.
        The Tool's name may only contain letters and numbers, and the Activity's name may only contain letters, numbers, and underscores.

        Args:
            activity: Activity to convert

        Returns:
            str: Native tool name.
        """
        tool_name = self.name
        if re.match(r"^[a-zA-Z0-9]+$", tool_name) is None:
            raise ValueError("Tool name can only contain letters and numbers.")

        activity_name = self.activity_name(activity)
        if re.match(r"^[a-zA-Z0-9_]+$", activity_name) is None:
            raise ValueError("Activity name can only contain letters, numbers, and underscores.")

        return f"{tool_name}_{activity_name}"

    def are_requirements_met(self, requirements_path: str) -> bool:
        requirements = Path(requirements_path).read_text().splitlines()

        try:
            for requirement in requirements:
                importlib.metadata.version(requirement)
            return True
        except importlib.metadata.PackageNotFoundError:
            return False
