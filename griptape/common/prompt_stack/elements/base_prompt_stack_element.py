from attrs import define, field
from abc import ABC


@define
class BasePromptStackElement(ABC):
    GENERIC_ROLE = "generic"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    role: str = field(kw_only=True, metadata={"serializable": True})

    def is_generic(self) -> bool:
        return self.role == self.GENERIC_ROLE

    def is_system(self) -> bool:
        return self.role == self.SYSTEM_ROLE

    def is_user(self) -> bool:
        return self.role == self.USER_ROLE

    def is_assistant(self) -> bool:
        return self.role == self.ASSISTANT_ROLE
