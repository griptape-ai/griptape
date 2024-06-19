from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import ActionArtifact, BaseArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.common import (
    ActionCallPromptStackContent,
    ActionResultPromptStackContent,
    BasePromptStackContent,
    ImagePromptStackContent,
    PromptStackMessage,
    TextPromptStackContent,
)
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define
class PromptStack(SerializableMixin):
    messages: list[PromptStackMessage] = field(factory=list, kw_only=True, metadata={"serializable": True})
    actions: list[BaseTool] = field(factory=list, kw_only=True)

    def add_message(self, artifact: str | BaseArtifact, role: str) -> PromptStackMessage:
        content = self.__process_artifact(artifact)

        self.messages.append(PromptStackMessage(content=content, role=role))

        return self.messages[-1]

    def add_system_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.SYSTEM_ROLE)

    def add_user_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.USER_ROLE)

    def add_assistant_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.ASSISTANT_ROLE)

    def add_action_call_message(
        self, thought: Optional[str], actions: list[ActionArtifact.Action]
    ) -> PromptStackMessage:
        thought_content = self.__process_artifact(thought) if thought else []

        action_calls_content = [ActionCallPromptStackContent(ActionArtifact(action)) for action in actions]

        self.messages.append(
            PromptStackMessage(
                content=[*thought_content, *action_calls_content], role=PromptStackMessage.ASSISTANT_ROLE
            )
        )

        return self.messages[-1]

    def add_action_result_message(
        self, instructions: Optional[str | BaseArtifact], actions: list[ActionArtifact.Action]
    ) -> PromptStackMessage:
        instructions_content = self.__process_artifact(instructions) if instructions else []

        action_results_content = [
            ActionResultPromptStackContent(action.output, action=action)
            for action in actions
            if action.output is not None
        ]

        self.messages.append(
            PromptStackMessage(
                content=[*action_results_content, *instructions_content], role=PromptStackMessage.USER_ROLE
            )
        )

        return self.messages[-1]

    def __process_artifact(self, artifact: str | BaseArtifact) -> list[BasePromptStackContent]:
        if isinstance(artifact, str):
            return [TextPromptStackContent(TextArtifact(artifact))]
        elif isinstance(artifact, TextArtifact):
            return [TextPromptStackContent(artifact)]
        elif isinstance(artifact, ImageArtifact):
            return [ImagePromptStackContent(artifact)]
        elif isinstance(artifact, ActionArtifact):
            return [ActionCallPromptStackContent(artifact)]
        elif isinstance(artifact, ListArtifact):
            processed_contents = [self.__process_artifact(artifact) for artifact in artifact.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
