from attr import define, field
from griptape.drivers import BaseConversationMemoryDriver
from griptape.memory.structure import ConversationMemory


@define
class LocalConversationMemoryDriver(BaseConversationMemoryDriver):
    file_path: str = field(default="griptape_memory.json", kw_only=True)

    def store(self, memory: ConversationMemory) -> None:
        with open(self.file_path, "w") as file:
            file.write(memory.to_json())

    def load(self) -> ConversationMemory:
        with open(self.file_path, "r") as file:
            memory = ConversationMemory.from_json(file.read())

            memory.driver = self

            return memory
