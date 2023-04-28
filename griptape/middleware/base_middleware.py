from abc import ABC
from attr import define, field, Factory
from griptape.core import ActivityMixin


@define
class BaseMiddleware(ActivityMixin, ABC):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: bytes) -> bytes:
        return value

    def process_output(self, tool_activity: callable, value: bytes) -> bytes:
        return value
