from abc import ABC


class BaseQueryProcessor(ABC):
    def process(self, query: str) -> str:
        ...
