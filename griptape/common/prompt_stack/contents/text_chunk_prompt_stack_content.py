from attrs import define

from griptape.common import BaseChunkPromptStackContent


@define
class TextChunkPromptStackContent(BaseChunkPromptStackContent):
    chunk: str
