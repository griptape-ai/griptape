from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional, Union

from attrs import Factory, define, field

from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.common import BaseDeltaMessageContent, BaseMessageContent


@define
class BaseMessage(ABC, SerializableMixin):
    @define
    class Usage(SerializableMixin):
        input_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})
        output_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})

        @property
        def total_tokens(self) -> float:
            return (self.input_tokens or 0) + (self.output_tokens or 0)

        def __add__(self, other: BaseMessage.Usage) -> BaseMessage.Usage:
            return BaseMessage.Usage(
                input_tokens=(self.input_tokens or 0) + (other.input_tokens or 0),
                output_tokens=(self.output_tokens or 0) + (other.output_tokens or 0),
            )

    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    content: list[Union[BaseMessageContent, BaseDeltaMessageContent]] = field(metadata={"serializable": True})
    role: str = field(kw_only=True, metadata={"serializable": True})
    usage: Usage = field(kw_only=True, default=Factory(lambda: BaseMessage.Usage()), metadata={"serializable": True})

    def is_system(self) -> bool:
        return self.role == self.SYSTEM_ROLE

    def is_user(self) -> bool:
        return self.role == self.USER_ROLE

    def is_assistant(self) -> bool:
        return self.role == self.ASSISTANT_ROLE
