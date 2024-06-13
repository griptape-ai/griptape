from __future__ import annotations
from attrs import define, field

from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact, ImageArtifact
from griptape.mixins import SerializableMixin
from griptape.common import PromptStackElement, TextPromptStackContent, ImagePromptStackContent


@define
class PromptStack(SerializableMixin):
    inputs: list[PromptStackElement] = field(factory=list, kw_only=True, metadata={"serializable": True})

    def add_input(self, content: str | BaseArtifact, role: str) -> PromptStackElement:
        if isinstance(content, str):
            self.inputs.append(PromptStackElement(content=[TextPromptStackContent(TextArtifact(content))], role=role))
        elif isinstance(content, TextArtifact):
            self.inputs.append(PromptStackElement(content=[TextPromptStackContent(content)], role=role))
        elif isinstance(content, ListArtifact):
            contents = []
            for artifact in content.value:
                if isinstance(artifact, TextArtifact):
                    contents.append(TextPromptStackContent(artifact))
                elif isinstance(artifact, ImageArtifact):
                    contents.append(ImagePromptStackContent(artifact))
                else:
                    raise ValueError(f"Unsupported artifact type: {type(artifact)}")
            self.inputs.append(PromptStackElement(content=contents, role=role))
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

        return self.inputs[-1]

    def add_system_input(self, content: str) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.SYSTEM_ROLE)

    def add_user_input(self, content: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.USER_ROLE)

    def add_assistant_input(self, content: str) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.ASSISTANT_ROLE)
