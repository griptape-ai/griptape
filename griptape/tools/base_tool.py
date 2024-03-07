from __future__ import annotations
import logging
import subprocess
import sys
from typing import TYPE_CHECKING, Callable
from schema import Schema, Literal, Or
import inspect
import os
from abc import ABC
from typing import Optional
import yaml
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, InfoArtifact, TextArtifact
from griptape.mixins import ActivityMixin
import xml.etree.ElementTree as ET

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tasks import ActionSubtask


@define
class BaseTool(ActivityMixin, ABC):
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

    MANIFEST_FILE = "manifest.yml"
    REQUIREMENTS_FILE = "requirements.txt"

    name: str = field(
        default=Factory(lambda self: self.class_name, takes_self=True),
        kw_only=True,
    )
    input_memory: Optional[list[TaskMemory]] = field(
        default=None, kw_only=True
    )
    output_memory: Optional[dict[str, list[TaskMemory]]] = field(
        default=None, kw_only=True
    )
    install_dependencies_on_init: bool = field(default=True, kw_only=True)
    dependencies_install_directory: Optional[str] = field(
        default=None, kw_only=True
    )
    verbose: bool = field(default=False, kw_only=True)
    off_prompt: bool = field(default=True, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.install_dependencies_on_init:
            self.install_dependencies(os.environ.copy())

    @output_memory.validator  # pyright: ignore
    def validate_output_memory(
        self, _, output_memory: dict[str, Optional[list[TaskMemory]]]
    ) -> None:
        if output_memory:
            for activity_name, memory_list in output_memory.items():
                if not self.find_activity(activity_name):
                    raise ValueError(f"activity {activity_name} doesn't exist")
                if memory_list is None:
                    raise ValueError(
                        f"memory list for activity '{activity_name}' can't be None"
                    )

                output_memory_names = [memory.name for memory in memory_list]

                if len(output_memory_names) > len(set(output_memory_names)):
                    raise ValueError(
                        f"memory names have to be unique in activity '{activity_name}' output"
                    )

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
        with open(self.manifest_path) as yaml_file:
            return yaml.safe_load(yaml_file)

    @property
    def abs_file_path(self):
        return os.path.abspath(inspect.getfile(self.__class__))

    @property
    def abs_dir_path(self):
        return os.path.dirname(self.abs_file_path)

    # This method has to remain a method and can't be decorated with @property because
    # of the max depth recursion issue in `self.activities`.
    def schema(self):
        action_schemas = [
            Schema(
                {
                    Literal("name"): self.name,
                    Literal(
                        "path", description=self.activity_description(activity)
                    ): self.activity_name(activity),
                    **self.activity_to_input(
                        activity
                    ),  # Unpack the dictionary in order to only add the key-values if there are any
                }
            )
            for activity in self.activities()
        ]
        full_schema = Schema(
            Or(*action_schemas), description=f"{self.name} action schema."
        )

        test = str(full_schema.json_schema(f"{self.name} Action Schema"))

        return self.dict_to_xml(
            full_schema.json_schema(f"{self.name} Action Schema")
        )

    # return full_schema.json_schema(f"{self.name} Action Schema")

    def execute(
        self, activity: Callable, subtask: ActionSubtask
    ) -> BaseArtifact:
        preprocessed_input = self.before_run(activity, subtask.action_input)
        output = self.run(activity, subtask, preprocessed_input)
        postprocessed_output = self.after_run(activity, subtask, output)

        return postprocessed_output

    def before_run(
        self, activity: Callable, value: Optional[dict]
    ) -> Optional[dict]:
        return value

    def run(
        self, activity: Callable, subtask: ActionSubtask, value: Optional[dict]
    ) -> BaseArtifact:
        activity_result = activity(value)

        if isinstance(activity_result, BaseArtifact):
            result = activity_result
        else:
            logging.warning(
                "Activity result is not an artifact; converting result to InfoArtifact"
            )

            result = InfoArtifact(activity_result)

        return result

    def after_run(
        self, activity: Callable, subtask: ActionSubtask, value: BaseArtifact
    ) -> BaseArtifact:
        if value:
            if self.output_memory:
                output_memories = (
                    self.output_memory[getattr(activity, "name")] or []
                )
                for memory in output_memories:
                    value = memory.process_output(activity, subtask, value)

                if isinstance(value, BaseArtifact):
                    return value
                else:
                    return TextArtifact(str(value))
            else:
                return value
        else:
            return InfoArtifact("Tool returned an empty value")

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

    def install_dependencies(
        self, env: Optional[dict[str, str]] = None
    ) -> None:
        env = env if env else {}

        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
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
            stderr=None if self.verbose else subprocess.DEVNULL,
        )

    def find_input_memory(self, memory_name: str) -> Optional[TaskMemory]:
        if self.input_memory:
            return next(
                (m for m in self.input_memory if m.name == memory_name), None
            )
        else:
            return None

    def dict_to_xml(self, schema_dict: dict):
        def add_parameters(properties, required, parameters_section):
            for param_name, param_info in properties.items():
                if param_name in required:
                    parameter = ET.SubElement(parameters_section, "parameter")
                    ET.SubElement(parameter, "name").text = param_name
                    param_type = param_info.get(
                        "type", "string"
                    )  # Default type is string
                    ET.SubElement(parameter, "type").text = param_type
                    description = param_info.get("description", "")
                    if description:
                        ET.SubElement(parameter, "description").text = (
                            description
                        )

        root = ET.Element("tool_description")

        # Tool name and description
        ET.SubElement(root, "tool_name").text = schema_dict.get(
            "$id", ""
        ).replace(" Action Schema", "")
        ET.SubElement(root, "description").text = schema_dict.get(
            "description", ""
        )

        parameters_section = ET.SubElement(root, "parameters")

        if "properties" in schema_dict:
            properties = schema_dict.get("properties", {})
            required = schema_dict.get("required", [])
            add_parameters(properties, required, parameters_section)
        elif "anyOf" in schema_dict:
            for option in schema_dict["anyOf"]:
                properties = option.get("properties", {})
                required = option.get("required", [])
                add_parameters(properties, required, parameters_section)
                # Handle nested properties like 'input' if necessary

        def prettify(element, indent="    "):
            queue = [(0, element)]  # (level, element)
            while queue:
                level, element = queue.pop(0)
                children = [(level + 1, child) for child in list(element)]
                if children:
                    element.text = "\n" + indent * (
                        level + 1
                    )  # for child open
                if queue:
                    element.tail = (
                        "\n" + indent * queue[0][0]
                    )  # for next sibling
                else:
                    element.tail = "\n" + indent * (
                        level - 1
                    )  # for close of parent
                queue[0:0] = children  # add children to the start of the queue

        prettify(root)
        return ET.tostring(root, encoding="unicode")
