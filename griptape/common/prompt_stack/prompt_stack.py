from __future__ import annotations
from attrs import define, field

from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact, ImageArtifact
from griptape.mixins import SerializableMixin
from griptape.common import PromptStackElement, TextPromptStackContent, BasePromptStackContent, ImagePromptStackContent


@define
class PromptStack(SerializableMixin):
    inputs: list[PromptStackElement] = field(factory=list, kw_only=True, metadata={"serializable": True})

    def add_input(self, content: str | BaseArtifact, role: str) -> PromptStackElement:
        new_content = self.__process_content(content)

        self.inputs.append(PromptStackElement(content=new_content, role=role))

        return self.inputs[-1]

    def add_system_input(self, content: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.SYSTEM_ROLE)

    def add_user_input(self, content: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.USER_ROLE)

    def add_assistant_input(self, content: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.ASSISTANT_ROLE)

    def __process_content(self, content: str | BaseArtifact) -> list[BasePromptStackContent]:
        if isinstance(content, str):
            return [TextPromptStackContent(TextArtifact(content))]
        elif isinstance(content, TextArtifact):
            return [TextPromptStackContent(content)]
        elif isinstance(content, ImageArtifact):
            return [ImagePromptStackContent(content)]
        elif isinstance(content, ListArtifact):
            processed_contents = [self.__process_content(artifact) for artifact in content.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
