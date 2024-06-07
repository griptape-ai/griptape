from abc import ABC
from typing import Any

from attrs import define

from griptape.mixins import SerializableMixin


@define
class BasePromptStackContent(ABC, SerializableMixin):
    value: Any

    def __str__(self) -> str:
        return str(self.value)
