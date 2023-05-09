from abc import ABC
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact
from griptape.core import ActivityMixin


@define
class BaseRamp(ActivityMixin, ABC):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        return value

    def process_output(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        return value
