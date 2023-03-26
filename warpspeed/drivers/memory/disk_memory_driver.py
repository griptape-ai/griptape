from attrs import define, field
from warpspeed.drivers import MemoryDriver
from warpspeed.memory import PipelineMemory


@define
class DiskMemoryDriver(MemoryDriver):
    file_path: str = field(default="warpspeed_memory.json", kw_only=True)

    def store(self, memory: PipelineMemory) -> None:
        with open(self.file_path, "w") as file:
            file.write(memory.to_json())

    def load(self) -> PipelineMemory:
        with open(self.file_path, "r") as file:
            memory = PipelineMemory.from_json(file.read())

            memory.driver = self

            return memory
