from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.memory.meta import BaseMetaEntry


@define
class ActionSubtaskMetaEntry(BaseMetaEntry):
    """Used to store ActionSubtask data to preserve TaskMemory pointers and context in the form of thought and action.

    Attributes:
        thought: CoT thought string from the LLM.
        actions: ReAct actions JSON string from the LLM.
        answer: tool-generated and memory-processed response from Griptape.
    """

    type: str = field(default=BaseMetaEntry.__name__, kw_only=True, metadata={"serializable": False})
    thought: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    actions: str = field(kw_only=True, metadata={"serializable": True})
    answer: str = field(kw_only=True, metadata={"serializable": True})
