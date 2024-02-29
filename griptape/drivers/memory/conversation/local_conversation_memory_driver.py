import os
from attr import define, field
from typing import Optional
from griptape.drivers import BaseConversationMemoryDriver
from griptape.memory.structure import BaseConversationMemory


@define
class LocalConversationMemoryDriver(BaseConversationMemoryDriver):
    file_path: str = field(default="griptape_memory.json", kw_only=True, metadata={"serializable": True})

    def store(self, memory: BaseConversationMemory) -> None:
        with open(self.file_path, "w") as file:
            file.write(memory.to_json())

    def load(self) -> Optional[BaseConversationMemory]:
        if not os.path.exists(self.file_path):
            return None
        with open(self.file_path) as file:
            memory = BaseConversationMemory.from_json(file.read())

            memory.driver = self

            return memory
