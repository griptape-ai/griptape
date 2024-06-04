from typing import Any
from attrs import define, field

from griptape.common import BasePromptStackContent


@define
class BaseChunkPromptStackContent(BasePromptStackContent):
    value: Any = field()
