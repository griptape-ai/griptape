import inspect
import logging
import os
from abc import ABC
from typing import Optional
import yaml
from attr import define, fields, Attribute, field, Factory
import attrs
from decouple import config
from jinja2 import Template
from griptape.middleware import BaseMiddleware


@define
class BaseTool(ABC):
    MANIFEST_FILE = "manifest.yml"
    DOCKERFILE_FILE = "Dockerfile"
    REQUIREMENTS_FILE = "requirements.txt"

    name: str = field(default=Factory(lambda self: self.class_name, takes_self=True), kw_only=True)
    metadata: Optional[str] = field(default=None, kw_only=True)
    middleware: dict[callable, BaseMiddleware] = field(factory=dict, kw_only=True)

    # Disable logging, unless it's an error, so that executors don't capture it as subprocess output.
    logging.basicConfig(level=logging.ERROR)

    def __attrs_post_init__(self):
        attrs.resolve_types(self.__class__, globals(), locals())

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def env_fields(self) -> list[Attribute]:
        return [f for f in fields(self.__class__) if f.metadata.get("env")]

    @property
    def env(self) -> dict[str, str]:
        return {
            f.metadata["env"]: str(getattr(self, f.name)) for f in self.env_fields if getattr(self, f.name)
        }

    @property
    def manifest_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.MANIFEST_FILE)

    @property
    def dockerfile_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.DOCKERFILE_FILE)

    @property
    def requirements_path(self) -> str:
        return os.path.join(self.abs_dir_path, self.REQUIREMENTS_FILE)

    @property
    def manifest(self) -> dict:
        with open(self.manifest_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)

    @property
    def dockerfile(self) -> Optional[str]:
        if os.path.exists(self.dockerfile_path):
            with open(self.dockerfile_path, "r") as dockerfile:
                return dockerfile.read()
        else:
            return None

    @property
    def abs_file_path(self):
        return os.path.abspath(inspect.getfile(self.__class__))

    @property
    def abs_dir_path(self):
        return os.path.dirname(self.abs_file_path)

    @property
    def schema_template_args(self) -> dict:
        return {}

    def actions(self) -> list[callable]:
        methods = []

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "is_action", False):
                methods.append(method)

        return methods

    def env_value(self, name: str) -> Optional[any]:
        # First, check if there is a matching field with an environment variable in the metadata
        env_field = next(
            (f for f in self.env_fields if f.metadata.get("env") == name),
            None
        )

        if env_field:
            # Try casting the environment variable value to a matching field type
            type_hint = env_field.type.__args__[0] if hasattr(env_field.type, "__args__") else env_field.type
            env_var_value = config(name, default=None, cast=type_hint) if config(name, default=None) else None
        else:
            env_var_value = config(name, default=None)

        if env_var_value:
            # Return a non-None environment variable value
            return env_var_value
        elif env_field:
            # Read field value directly
            return getattr(self, env_field.name)
        else:
            # If all fails, return None
            return None

    def action_name(self, action: callable) -> str:
        if action is None or not getattr(action, "is_action", False):
            raise Exception("This method is not a tool action.")
        else:
            return action.config["name"]

    def action_description(self, action: callable) -> str:
        if action is None or not getattr(action, "is_action", False):
            raise Exception("This method is not a tool action.")
        else:
            description_lines = [
                Template(action.config["description"]).render(self.schema_template_args),
                f"Input Schema: {self.action_schema(action)}"
            ]

            if self.metadata:
                description_lines.append(
                    f"Additional metadata: {self.metadata}"
                )

            return str.join("\n", description_lines)

    def action_schema(self, action: callable) -> dict:
        if action is None or not getattr(action, "is_action", False):
            raise Exception("This method is not a tool action.")
        else:
            return action.config["schema"].json_schema("ToolInputSchema")

    def validate(self) -> bool:
        from griptape.utils import ManifestValidator

        if not os.path.exists(self.manifest_path):
            raise Exception(f"{self.MANIFEST_FILE} not found")

        if not os.path.exists(self.requirements_path):
            raise Exception(f"{self.REQUIREMENTS_FILE} not found")

        ManifestValidator().validate(self.manifest)

        return True
