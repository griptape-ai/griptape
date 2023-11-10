from __future__ import annotations
from attr import field, define
from griptape.memory.meta import BaseMetaEntry


@define
class ActionSubtaskMetaEntry(BaseMetaEntry):
    thought: str = field(kw_only=True)
    action: str = field(kw_only=True)
    answer: str = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import ActionSubtaskMetaEntrySchema

        return dict(ActionSubtaskMetaEntrySchema().dump(self))
