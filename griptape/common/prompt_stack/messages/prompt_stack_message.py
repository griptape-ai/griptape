from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import BasePromptStackContent, TextPromptStackContent

from .base_prompt_stack_message import BasePromptStackMessage


@define
class PromptStackMessage(BasePromptStackMessage):
    def __init__(self, content: str | list[BasePromptStackContent], **kwargs: Any):
        if isinstance(content, str):
            content = [TextPromptStackContent(TextArtifact(value=content))]
        self.__attrs_init__(content, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

    content: list[BasePromptStackContent] = field(metadata={"serializable": True})

    @property
    def value(self) -> Any:
        if len(self.content) == 1:
            return self.content[0].artifact.value
        else:
            return [content.artifact for content in self.content]

    def __str__(self) -> str:
        return self.to_text()

    def to_text(self) -> str:
        return self.to_text_artifact().to_text()

    def to_text_artifact(self) -> TextArtifact:
        return TextArtifact(
            "".join(
                [content.artifact.to_text() for content in self.content if isinstance(content, TextPromptStackContent)]
            )
        )
