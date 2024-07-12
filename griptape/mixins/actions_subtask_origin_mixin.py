from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from attrs import define
from schema import Literal, Schema

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tasks import ActionsSubtask
    from griptape.tools import BaseTool


@define(slots=False)
class ActionsSubtaskOriginMixin:
    @abstractmethod
    def find_tool(self, tool_name: str) -> BaseTool: ...

    @abstractmethod
    def find_memory(self, memory_name: str) -> TaskMemory: ...

    @abstractmethod
    def find_subtask(self, subtask_id: str) -> ActionsSubtask: ...

    @abstractmethod
    def add_subtask(self, subtask: ActionsSubtask) -> ActionsSubtask: ...

    @abstractmethod
    def actions_schema(self) -> Schema: ...

    def _actions_schema_for_tools(self, tools: list[BaseTool]) -> Schema:
        action_schemas = []

        for tool in tools:
            for activity_schema in tool.activity_schemas():
                action_schema = activity_schema.schema
                tag_key = Literal("tag", description="Unique tag name for action execution.")

                action_schema[tag_key] = str

                action_schemas.append(action_schema)

        return Schema(description="JSON schema for an array of actions.", schema=action_schemas)
