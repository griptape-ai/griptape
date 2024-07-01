from __future__ import annotations
from attrs import define, field

from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact, ImageArtifact
from griptape.mixins import SerializableMixin
from griptape.common import Message, TextMessageContent, BaseMessageContent, ImageMessageContent


@define
class PromptStack(SerializableMixin):
    messages: list[Message] = field(factory=list, kw_only=True, metadata={"serializable": True})

    @property
    def system_messages(self) -> list[Message]:
        return [message for message in self.messages if message.is_system()]

    @property
    def user_messages(self) -> list[Message]:
        return [message for message in self.messages if message.is_user()]

    @property
    def assistant_messages(self) -> list[Message]:
        return [message for message in self.messages if message.is_assistant()]

    def add_message(self, artifact: str | BaseArtifact, role: str) -> Message:
        new_content = self.__process_artifact(artifact)

        self.messages.append(Message(content=new_content, role=role))

        return self.messages[-1]

    def add_system_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.SYSTEM_ROLE)

    def add_user_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.USER_ROLE)

    def add_assistant_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.ASSISTANT_ROLE)

    def __process_artifact(self, artifact: str | BaseArtifact) -> list[BaseMessageContent]:
        if isinstance(artifact, str):
            return [TextMessageContent(TextArtifact(artifact))]
        elif isinstance(artifact, TextArtifact):
            return [TextMessageContent(artifact)]
        elif isinstance(artifact, ImageArtifact):
            return [ImageMessageContent(artifact)]
        elif isinstance(artifact, ListArtifact):
            processed_contents = [self.__process_artifact(artifact) for artifact in artifact.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
