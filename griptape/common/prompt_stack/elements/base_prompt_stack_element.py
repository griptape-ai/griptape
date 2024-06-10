from attrs import define, field, Factory
from abc import ABC, abstractmethod


@define
class BasePromptStackElement(ABC):
    GENERIC_ROLE = "generic"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    @define
    class Usage:
        input_tokens: int = field(kw_only=True, default=0, metadata={"serializable": True})
        output_tokens: int = field(kw_only=True, default=0, metadata={"serializable": True})

        @property
        def total_tokens(self) -> int:
            return self.input_tokens + self.output_tokens

    role: str = field(kw_only=True, metadata={"serializable": True})
    usage: Usage = field(
        kw_only=True, default=Factory(lambda: BasePromptStackElement.Usage()), metadata={"serializable": True}
    )

    def is_generic(self) -> bool:
        return self.role == self.GENERIC_ROLE

    def is_system(self) -> bool:
        return self.role == self.SYSTEM_ROLE

    def is_user(self) -> bool:
        return self.role == self.USER_ROLE

    def is_assistant(self) -> bool:
        return self.role == self.ASSISTANT_ROLE

    @abstractmethod
    def to_text(self) -> str: ...
