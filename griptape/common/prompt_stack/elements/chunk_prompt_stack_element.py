from typing import Optional

from attrs import define, field

from griptape.common import BaseChunkPromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class ChunkPromptStackElement(BasePromptStackElement):
    index: int = field(kw_only=True, metadata={"serializable": True})
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    chunk: Optional[BaseChunkPromptStackContent] = field(kw_only=True, default=None, metadata={"serializable": True})
