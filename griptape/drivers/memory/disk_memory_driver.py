from attr import define, field
from griptape.drivers import MemoryDriver
from griptape.memory import Memory


@define
class DiskMemoryDriver(MemoryDriver):
    file_path: str = field(default="griptape_memory.json", kw_only=True)

    def store(self, memory: Memory) -> None:
        with open(self.file_path, "w") as file:
            file.write(memory.to_json())

    def load(self) -> Memory:
        with open(self.file_path, "r") as file:
            memory = Memory.from_json(file.read())

            memory.driver = self

            return memory
