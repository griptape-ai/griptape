from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.artifacts.action_call_artifact import ActionCallArtifact
from griptape.common import ImagePromptStackContent, PromptStackElement, TextPromptStackContent, BasePromptStackContent
from griptape.common.prompt_stack.contents.action_call_prompt_stack_content import ActionCallPromptStackContent
from griptape.common.prompt_stack.contents.action_result_prompt_stack_content import ActionResultPromptStackContent
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.tasks.actions_subtask import ActionsSubtask
    from griptape.tools import BaseTool


@define
class PromptStack(SerializableMixin):
    inputs: list[PromptStackElement] = field(factory=list, kw_only=True, metadata={"serializable": True})
    actions: list[BaseTool] = field(factory=list, kw_only=True)

    def add_input(self, artifact: str | BaseArtifact, role: str) -> PromptStackElement:
        content = self.__process_artifact(artifact)

        self.inputs.append(PromptStackElement(content=content, role=role))

        return self.messages[-1]

    def add_system_input(self, artifact: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(artifact, PromptStackElement.SYSTEM_ROLE)

    def add_user_input(self, artifact: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(artifact, PromptStackElement.USER_ROLE)

    def add_assistant_input(self, artifact: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(artifact, PromptStackElement.ASSISTANT_ROLE)

    def add_action_call_input(self, thought: Optional[str], actions: list[ActionsSubtask.Action]) -> PromptStackElement:
        thought_content = self.__process_artifact(thought) if thought else []

        action_calls_content = [
            ActionCallPromptStackContent(
                ActionCallArtifact(
                    ActionCallArtifact.ActionCall(
                        tag=action.tag, name=action.name, path=action.path, input=json.dumps(action.input)
                    )
                )
            )
            for action in actions
        ]

        self.inputs.append(
            PromptStackElement(
                content=[*thought_content, *action_calls_content], role=PromptStackElement.ASSISTANT_ROLE
            )
        )

        return self.inputs[-1]

    def add_action_result_input(
        self, instructions: Optional[str | BaseArtifact], actions: list[ActionsSubtask.Action]
    ) -> PromptStackElement:
        instructions_content = self.__process_artifact(instructions) if instructions else []

        action_results_content = [
            ActionResultPromptStackContent(
                action.output,
                action_tag=action.tag,
                action_name=action.name,
                action_path=action.path,
                action_input=action.input,
            )
            for action in actions
            if action.output is not None
        ]

        self.inputs.append(
            PromptStackElement(
                content=[*action_results_content, *instructions_content], role=PromptStackElement.USER_ROLE
            )
        )

        return self.inputs[-1]

    def __process_artifact(self, artifact: str | BaseArtifact) -> list[BasePromptStackContent]:
        if isinstance(artifact, str):
            return [TextPromptStackContent(TextArtifact(artifact))]
        elif isinstance(artifact, TextArtifact):
            return [TextPromptStackContent(artifact)]
        elif isinstance(artifact, ImageArtifact):
            return [ImagePromptStackContent(artifact)]
        elif isinstance(artifact, ActionCallArtifact):
            return [ActionCallPromptStackContent(artifact)]
        elif isinstance(artifact, ListArtifact):
            processed_contents = [self.__process_artifact(artifact) for artifact in artifact.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
