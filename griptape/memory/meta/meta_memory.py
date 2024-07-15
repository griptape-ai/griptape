from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from griptape.memory.meta import BaseMetaEntry


@define
class MetaMemory:
    """Used to store meta entries that can be shared between tasks.

    Attributes:
        entries: a list of meta entries for downstream tasks and subtasks to load.
    """

    entries: list[BaseMetaEntry] = field(factory=list, kw_only=True)

    def add_entry(self, entry: BaseMetaEntry) -> None:
        self.entries.append(entry)
