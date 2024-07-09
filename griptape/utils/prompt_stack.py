from __future__ import annotations
from attrs import define, field

from griptape.mixins import SerializableMixin


@define
class PromptStack(SerializableMixin):
    GENERIC_ROLE = "generic"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    @define
    class Input(SerializableMixin):
        content: str = field(metadata={"serializable": True})
        role: str = field(metadata={"serializable": True})

        def is_generic(self) -> bool:
            return self.role == PromptStack.GENERIC_ROLE

        def is_system(self) -> bool:
            return self.role == PromptStack.SYSTEM_ROLE

        def is_user(self) -> bool:
            return self.role == PromptStack.USER_ROLE

        def is_assistant(self) -> bool:
            return self.role == PromptStack.ASSISTANT_ROLE

    inputs: list[Input] = field(factory=list, kw_only=True, metadata={"serializable": True})

    def add_input(self, content: str, role: str) -> Input:
        self.inputs.append(self.Input(content=content, role=role))

        return self.inputs[-1]

    def add_generic_input(self, content: str) -> Input:
        return self.add_input(content, self.GENERIC_ROLE)

    def add_system_input(self, content: str) -> Input:
        return self.add_input(content, self.SYSTEM_ROLE)

    def add_user_input(self, content: str) -> Input:
        return self.add_input(content, self.USER_ROLE)

    def add_assistant_input(self, content: str) -> Input:
        return self.add_input(content, self.ASSISTANT_ROLE)
