from attr import define, field
from griptape.memory.meta import BaseMetaEntry


@define
class MetaMemory:
    entries: list[BaseMetaEntry] = field(factory=list, kw_only=True)

    def add_entry(self, entry: BaseMetaEntry) -> None:
        self.entries.append(entry)
