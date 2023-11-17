from __future__ import annotations
from typing import Optional
from attr import field, define
from griptape.memory.meta import BaseMetaEntry


@define
class TaskMemoryMetaEntry(BaseMetaEntry):
    """

    Attributes:
        input_artifact_namespace: CoT thought string from the LLM.
        output_artifact_namespace: ReAct action JSON string from the LLM.
        answer: tool-generated and memory-processed response from Griptape.
    """

    output: Optional[str] = field(default=None, kw_only=True)
    task_memory_name: Optional[str] = field(default=None, kw_only=True)
    task_output_name: Optional[str] = field(default=None, kw_only=True)
    output_artifact_namespace: Optional[str] = field(default=None, kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import TaskMemoryMetaEntrySchema

        return dict(TaskMemoryMetaEntrySchema().dump(self))
