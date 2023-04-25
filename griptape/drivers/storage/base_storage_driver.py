from abc import ABC, abstractmethod
from typing import Optional


class BaseStorageDriver(ABC):
    @abstractmethod
    def save(self, value: any) -> str:
        ...

    @abstractmethod
    def load(self, key: str) -> Optional[any]:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
