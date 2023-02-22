from abc import ABC, abstractmethod


class Tool(ABC):
    description: str
    examples: str

    @abstractmethod
    def run(self, value: str) -> str:
        pass
