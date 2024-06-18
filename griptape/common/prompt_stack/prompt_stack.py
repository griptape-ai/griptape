from __future__ import annotations
from attrs import define, field

from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact, ImageArtifact
from griptape.mixins import SerializableMixin
from griptape.common import PromptStackMessage, TextPromptStackContent, BasePromptStackContent, ImagePromptStackContent


@define
class PromptStack(SerializableMixin):
    messages: list[PromptStackMessage] = field(factory=list, kw_only=True, metadata={"serializable": True})

    def add_message(self, artifact: str | BaseArtifact, role: str) -> PromptStackMessage:
        new_content = self.__process_artifact(artifact)

        self.messages.append(PromptStackMessage(content=new_content, role=role))

        return self.messages[-1]

    def add_system_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.SYSTEM_ROLE)

    def add_user_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.USER_ROLE)

    def add_assistant_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.ASSISTANT_ROLE)

    def __process_artifact(self, artifact: str | BaseArtifact) -> list[BasePromptStackContent]:
        if isinstance(artifact, str):
            return [TextPromptStackContent(TextArtifact(artifact))]
        elif isinstance(artifact, TextArtifact):
            return [TextPromptStackContent(artifact)]
        elif isinstance(artifact, ImageArtifact):
            return [ImagePromptStackContent(artifact)]
        elif isinstance(artifact, ListArtifact):
            processed_contents = [self.__process_artifact(artifact) for artifact in artifact.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
