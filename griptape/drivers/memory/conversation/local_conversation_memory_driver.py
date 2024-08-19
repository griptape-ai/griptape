from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.drivers import BaseConversationMemoryDriver

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


@define
class LocalConversationMemoryDriver(BaseConversationMemoryDriver):
    file_path: str = field(default="griptape_memory.json", kw_only=True, metadata={"serializable": True})

    def store(self, memory: BaseConversationMemory) -> None:
        Path(self.file_path).write_text(memory.to_json())

    def load(self) -> Optional[BaseConversationMemory]:
        from griptape.memory.structure import BaseConversationMemory

        if not os.path.exists(self.file_path):
            return None

        memory_dict = json.loads(Path(self.file_path).read_text())
        # needed to avoid recursive method calls
        memory_dict["autoload"] = False
        memory = BaseConversationMemory.from_dict(memory_dict)

        memory.driver = self

        return memory
