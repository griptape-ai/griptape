from __future__ import annotations
import json
import time
from abc import ABC, abstractmethod
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError
from attr import define, field, Factory


@define
class BaseEvent(ABC):
    timestamp: float = field(default=Factory(lambda: time.time()), kw_only=True)
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls, event_dict: dict) -> BaseEvent:
        from griptape.schemas import (
            StartPromptEventSchema,
            FinishPromptEventSchema,
            StartTaskEventSchema,
            FinishTaskEventSchema,
            StartActionSubtaskEventSchema,
            FinishActionSubtaskEventSchema,
            StartStructureRunEventSchema,
            FinishStructureRunEventSchema,
            CompletionChunkEventSchema,
        )

        class_registry.register("StartPromptEvent", StartPromptEventSchema)
        class_registry.register("FinishPromptEvent", FinishPromptEventSchema)
        class_registry.register("StartTaskEvent", StartTaskEventSchema)
        class_registry.register("FinishTaskEvent", FinishTaskEventSchema)
        class_registry.register("StartActionSubtaskEvent", StartActionSubtaskEventSchema)
        class_registry.register("FinishActionSubtaskEvent", FinishActionSubtaskEventSchema)
        class_registry.register("StartStructureRunEvent", StartStructureRunEventSchema)
        class_registry.register("FinishStructureRunEvent", FinishStructureRunEventSchema)
        class_registry.register("CompletionChunkEvent", CompletionChunkEventSchema)

        try:
            return class_registry.get_class(event_dict["type"])().load(event_dict)
        except RegistryError:
            raise ValueError("Unsupported event type")

    @classmethod
    def from_json(cls, artifact_str: str) -> BaseEvent:
        return cls.from_dict(json.loads(artifact_str))

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_dict(self) -> dict:
        ...
