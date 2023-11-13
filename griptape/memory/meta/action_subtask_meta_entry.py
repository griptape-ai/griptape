from __future__ import annotations
from attr import field, define
from griptape.memory.meta import BaseMetaEntry


@define
class ActionSubtaskMetaEntry(BaseMetaEntry):
    """Used to store ActionSubtask data to preserve TaskMemory pointers and context in the form of thought and action.

    Attributes:
        thought: CoT thought string from the LLM.
        action: ReAct action JSON string from the LLM.
        answer: tool-generated and memory-processed response from Griptape.
    """

    thought: str = field(kw_only=True)
    action: str = field(kw_only=True)
    answer: str = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import ActionSubtaskMetaEntrySchema

        return dict(ActionSubtaskMetaEntrySchema().dump(self))
