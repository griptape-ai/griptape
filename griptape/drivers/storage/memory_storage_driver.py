import uuid
from typing import Optional
from griptape.drivers import BaseStorageDriver
from attr import define, field


@define
class MemoryStorageDriver(BaseStorageDriver):
    memory: dict[str, any] = field(factory=dict, kw_only=True)

    def save(self, value: any) -> str:
        key = uuid.uuid4().hex

        self.memory[key] = value

        return key

    def load(self, key: str) -> Optional[any]:
        return self.memory.get(key, None)

    def delete(self, key: str) -> None:
        if key in self.memory:
            del self.memory[key]
