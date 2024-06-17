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

    def add_message(self, artifact: str | BaseArtifact, role: str) -> PromptStackMessage:
        new_content = self.__process_artifact(artifact)

        self.messages.append(PromptStackMessage(content=new_content, role=role))

        return self.messages[-1]

    def add_system_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.SYSTEM_ROLE)

    def add_user_input(self, content: str | BaseArtifact) -> PromptStackElement:
        return self.add_input(content, PromptStackElement.USER_ROLE)

    def add_assistant_message(self, artifact: str | BaseArtifact) -> PromptStackMessage:
        return self.add_message(artifact, PromptStackMessage.ASSISTANT_ROLE)

    def add_action_call_input(self, thought: Optional[str], actions: list[ActionsSubtask.Action]) -> PromptStackElement:
        thought_content = self.__process_content(thought) if thought else []

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
        instructions_content = self.__process_content(instructions) if instructions else []

        action_results_content = [
            ActionResultPromptStackContent(action.output, action_tag=action.tag)
            for action in actions
            if action.output is not None
        ]

        self.inputs.append(
            PromptStackElement(
                content=[*instructions_content, *action_results_content], role=PromptStackElement.USER_ROLE
            )
        )

        return self.inputs[-1]

    def __process_content(self, content: str | BaseArtifact) -> list[BasePromptStackContent]:
        if isinstance(content, str):
            return [TextPromptStackContent(TextArtifact(content))]
        elif isinstance(content, TextArtifact):
            return [TextPromptStackContent(content)]
        elif isinstance(content, ImageArtifact):
            return [ImagePromptStackContent(content)]
        elif isinstance(content, ActionCallArtifact):
            return [ActionCallPromptStackContent(content)]
        elif isinstance(content, ListArtifact):
            processed_contents = [self.__process_content(artifact) for artifact in content.value]
            flattened_content = [
                sub_content for processed_content in processed_contents for sub_content in processed_content
            ]

            return flattened_content
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")
