import inspect
import json
import os
from abc import ABC, abstractmethod
from typing import Optional
from warpspeed.utils import J2


class Tool(ABC):
    @abstractmethod
    def run(self, value: any) -> str:
        ...

    @property
    def schema_json(self) -> str:
        return J2(
            "schema.json",
            templates_dir=self.abs_dir_path
        ).render(
            **self.schema_kwargs
        )

    @property
    def schema(self) -> dict:
        return json.loads(self.schema_json)

    @property
    def name(self):
        return self.schema["title"]

    @property
    def description(self):
        return self.schema["description"]

    @property
    def examples(self) -> Optional[str]:
        templates_dir = self.abs_dir_path
        examples_file = "examples.j2"

        if os.path.exists(os.path.join(templates_dir, examples_file)):
            return J2(examples_file, templates_dir=templates_dir).render()
        else:
            return None

    @property
    def abs_file_path(self):
        return os.path.abspath(inspect.getfile(self.__class__))

    @property
    def abs_dir_path(self):
        return os.path.dirname(self.abs_file_path)

    @property
    def schema_kwargs(self) -> dict:
        return {}
