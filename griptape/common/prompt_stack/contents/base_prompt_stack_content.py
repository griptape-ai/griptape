from abc import ABC
from typing import Any

from attrs import define

from griptape.mixins import SerializableMixin


@define
class BasePromptStackContent(ABC, SerializableMixin):
    content: Any
