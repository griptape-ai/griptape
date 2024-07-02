from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact
from griptape.common import BaseMessageContent, TextMessageContent

from .base_message import BaseMessage


@define
class Message(BaseMessage):
    def __init__(self, content: str | list[BaseMessageContent], **kwargs: Any):
        if isinstance(content, str):
            content = [TextMessageContent(TextArtifact(value=content))]
        self.__attrs_init__(content, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

    content: list[BaseMessageContent] = field(metadata={"serializable": True})

    @property
    def value(self) -> Any:
        return self.to_artifact().value

    def __str__(self) -> str:
        return self.to_text()

    def to_text(self) -> str:
        return "".join(
            [content.artifact.to_text() for content in self.content if isinstance(content, TextMessageContent)]
        )

    def to_artifact(self) -> BaseArtifact:
        if len(self.content) == 1:
            return self.content[0].artifact
        else:
            return ListArtifact([content.artifact for content in self.content])
