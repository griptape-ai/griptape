from __future__ import annotations

from typing import Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import BasePromptStackContent, TextPromptStackContent
from griptape.mixins.serializable_mixin import SerializableMixin

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    @define
    class Usage(SerializableMixin):
        input_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})
        output_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})

        @property
        def total_tokens(self) -> float:
            return (self.input_tokens or 0) + (self.output_tokens or 0)

    def __init__(self, content: str | list[BasePromptStackContent], **kwargs: Any):
        if isinstance(content, str):
            content = [TextPromptStackContent(TextArtifact(value=content))]
        self.__attrs_init__(content, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

    content: list[BasePromptStackContent] = field(metadata={"serializable": True})
    usage: Usage = field(
        kw_only=True, default=Factory(lambda: PromptStackElement.Usage()), metadata={"serializable": True}
    )

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
        if all(isinstance(content, TextPromptStackContent) for content in self.content):
            artifact = TextArtifact(value="")

            for content in self.content:
                if isinstance(content, TextPromptStackContent):
                    artifact += content.artifact

            return artifact
        else:
            raise ValueError("Cannot convert to TextArtifact")
