from typing import Any
from attrs import define

from griptape.common.prompt_stack.contents import BasePromptStackContent


@define
class BaseChunkPromptStackContent(BasePromptStackContent):
    chunk: Any
