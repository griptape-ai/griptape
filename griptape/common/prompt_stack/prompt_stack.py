from __future__ import annotations
from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.mixins import SerializableMixin
from griptape.common import PromptStackElement, TextPromptStackContent


@define
class PromptStack(SerializableMixin):
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    inputs: list[PromptStackElement] = field(factory=list, kw_only=True, metadata={"serializable": True})

    def add_input(self, content: str, role: str) -> PromptStackElement:
        self.inputs.append(PromptStackElement(content=[TextPromptStackContent(TextArtifact(content))], role=role))

        return self.inputs[-1]

    def add_system_input(self, content: str) -> PromptStackElement:
        return self.add_input(content, self.SYSTEM_ROLE)

    def add_user_input(self, content: str) -> PromptStackElement:
        return self.add_input(content, self.USER_ROLE)

    def add_assistant_input(self, content: str) -> PromptStackElement:
        return self.add_input(content, self.ASSISTANT_ROLE)
