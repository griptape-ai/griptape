from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define

if TYPE_CHECKING:
    pass


@define
class BaseTextStorageDriver(ABC):
    @abstractmethod
    def save(self, value: any) -> str:
        ...

    @abstractmethod
    def load(self, key: str) -> Optional[any]:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
