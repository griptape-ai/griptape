from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    examples: str

    @abstractmethod
    def run(self, value: str) -> str:
        pass
