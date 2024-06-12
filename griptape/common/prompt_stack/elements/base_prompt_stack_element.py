from __future__ import annotations

from abc import ABC

from attrs import define, field

from griptape.mixins import SerializableMixin


@define
class BasePromptStackElement(ABC, SerializableMixin):
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    role: str = field(kw_only=True, metadata={"serializable": True})

    def is_system(self) -> bool:
        return self.role == self.SYSTEM_ROLE

    def is_user(self) -> bool:
        return self.role == self.USER_ROLE

    def is_assistant(self) -> bool:
        return self.role == self.ASSISTANT_ROLE
