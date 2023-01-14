from attrs import define

@define
class Memory:
    memories: list[str] = []

    def is_empty(self) -> bool:
        return len(self.memories) == 0
    
    def add_memory(self, memory: str) -> None:
        return self.memories.append(memory)
    
    def to_string(self):
        return "\n".join(self.memories)