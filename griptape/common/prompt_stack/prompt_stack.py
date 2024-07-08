from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import ActionArtifact, BaseArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.common import (
    ActionCallMessageContent,
    ActionResultMessageContent,
    BaseMessageContent,
    ImageMessageContent,
    Message,
    TextMessageContent,
)
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define
class PromptStack(SerializableMixin):
    messages: list[Message] = field(factory=list, kw_only=True, metadata={"serializable": True})
    actions: list[BaseTool] = field(factory=list, kw_only=True)

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
        content = self.__process_artifact(artifact)

        self.messages.append(Message(content=content, role=role))

        return self.messages[-1]

    def add_system_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.SYSTEM_ROLE)

    def add_user_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.USER_ROLE)

    def add_assistant_message(self, artifact: str | BaseArtifact) -> Message:
        return self.add_message(artifact, Message.ASSISTANT_ROLE)

    def add_action_call_message(self, thought: Optional[str], actions: list[ActionArtifact.Action]) -> Message:
        thought_content = self.__process_artifact(thought) if thought else []

        action_calls_content = [ActionCallMessageContent(ActionArtifact(action)) for action in actions]

        self.messages.append(Message(content=[*thought_content, *action_calls_content], role=Message.ASSISTANT_ROLE))

        return self.messages[-1]

    def add_action_result_message(
        self, instructions: Optional[str | TextArtifact], actions: list[ActionArtifact.Action]
    ) -> Message:
        instructions_content = self.__process_artifact(instructions) if instructions else []

        action_results_content = [
            ActionResultMessageContent(action.output, action=action) for action in actions if action.output is not None
        ]

        self.messages.append(Message(content=[*action_results_content, *instructions_content], role=Message.USER_ROLE))

        return self.messages[-1]

    def __process_artifact(self, artifact: str | BaseArtifact) -> list[BaseMessageContent]:
        if isinstance(artifact, str):
            return [TextMessageContent(TextArtifact(artifact))]
        elif isinstance(artifact, TextArtifact):
            return [TextMessageContent(artifact)]
        elif isinstance(artifact, ImageArtifact):
            return [ImageMessageContent(artifact)]
        elif isinstance(artifact, ActionArtifact):
            return [ActionCallMessageContent(artifact)]
        elif isinstance(artifact, ListArtifact):
            processed_contents = [self.__process_artifact(artifact) for artifact in artifact.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
