from __future__ import annotations

import json
from typing import Any, Optional
from collections.abc import Sequence

from attrs import define, field, Factory

from griptape.artifacts import TextArtifact
from griptape.common import BasePromptStackContent, TextPromptStackContent
from griptape.common.prompt_stack.contents.action_call_prompt_stack_content import ActionCallPromptStackContent
from griptape.common.prompt_stack.contents.action_result_prompt_stack_content import ActionResultPromptStackContent
from griptape.mixins.serializable_mixin import SerializableMixin

from .base_message import BaseMessage


@define
class Message(BaseMessage):
    @define
    class Usage(SerializableMixin):
        input_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})
        output_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})

        @property
        def total_tokens(self) -> float:
            return (self.input_tokens or 0) + (self.output_tokens or 0)

    def __init__(self, content: str | Sequence[BasePromptStackContent], **kwargs: Any):
        if isinstance(content, str):
            content = [TextPromptStackContent(TextArtifact(value=content))]
        self.__attrs_init__(content, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

    content: Sequence[BasePromptStackContent] = field(metadata={"serializable": True})
    usage: Usage = field(kw_only=True, default=Factory(lambda: Message.Usage()), metadata={"serializable": True})

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

    def has_action_results(self) -> bool:
        return any(isinstance(content, ActionResultPromptStackContent) for content in self.content)

    def has_action_calls(self) -> bool:
        return any(isinstance(content, ActionCallPromptStackContent) for content in self.content)

    def to_text_artifact(self) -> TextArtifact:
        action_call_contents = [
            content for content in self.content if isinstance(content, ActionCallPromptStackContent)
        ]
        text_contents = [content for content in self.content if isinstance(content, TextPromptStackContent)]

        text_output = "".join([content.artifact.value for content in text_contents])
        if action_call_contents:
            action_call_dicts = []
            for action_call_content in action_call_contents:
                action_call = action_call_content.artifact.value

                # Some LLMs don't support nested parameters and therefore won't generate "values"
                if "values" in action_call.input:
                    action_call_dict = action_call.to_dict()
                else:
                    action_call_dict = {**action_call.to_dict(), **{"input": {"values": action_call.input}}}
                action_call_dicts.append(action_call_dict)

            actions_output = json.dumps(action_call_dicts, indent=2)
            output = f"Actions: {actions_output}"

            if text_output:
                output = f"Thought: {text_output}\n{output}"
        else:
            output = text_output

        return TextArtifact(value=output)
