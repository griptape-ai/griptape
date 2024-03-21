from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod
from attr import define
from schema import Schema, Literal

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tools import BaseTool
    from griptape.tasks import ActionsSubtask


@define(slots=False)
class ActionsSubtaskOriginMixin:
    @abstractmethod
    def find_tool(self, tool_name: str) -> BaseTool:
        ...

    @abstractmethod
    def find_memory(self, memory_name: str) -> TaskMemory:
        ...

    @abstractmethod
    def find_subtask(self, subtask_id: str) -> ActionsSubtask:
        ...

    @abstractmethod
    def add_subtask(self, subtask: ActionsSubtask) -> ActionsSubtask:
        ...

    @abstractmethod
    def actions_schema(self) -> dict:
        ...

    def _actions_schema_for_tools(self, tools: list[BaseTool]) -> dict:
        action_schemas = []

        for tool in tools:
            for activity_schema in tool.activity_schemas():
                action_schema = activity_schema.schema
                output_label_key = Literal(
                    "output_label", description="Label to identify action output. "
                                                "output_label values should NEVER be referenced in other action input"
                                                " values."
                )

                action_schema[output_label_key] = str

                action_schemas.append(action_schema)

        actions_schema = Schema(
            description="JSON schema for an array of actions to be executed in parallel.", schema=action_schemas
        )

        return actions_schema.json_schema("Actions Schema")
