from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from attrs import define, field

from griptape.drivers import BaseConversationMemoryDriver
from griptape.memory.structure import BaseConversationMemory


@define
class LocalConversationMemoryDriver(BaseConversationMemoryDriver):
    file_path: str = field(default="griptape_memory.json", kw_only=True, metadata={"serializable": True})

    def store(self, memory: BaseConversationMemory) -> None:
        Path(self.file_path).write_text(memory.to_json())

    def load(self) -> Optional[BaseConversationMemory]:
        if not os.path.exists(self.file_path):
            return None
        memory = BaseConversationMemory.from_json(Path(self.file_path).read_text())

        memory.driver = self

        return memory
