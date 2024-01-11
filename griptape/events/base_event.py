from __future__ import annotations
import time
from abc import ABC
from marshmallow import Schema, class_registry
from attr import define, field, Factory

from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema


@define
class BaseEvent(SerializableMixin, ABC):
    timestamp: float = field(default=Factory(lambda: time.time()), kw_only=True, metadata={"serialize": True})

    @classmethod
    def try_get_schema(cls, obj_type: str) -> list[type[Schema]] | type[Schema]:
        from griptape.events import (
            StartPromptEvent,
            FinishPromptEvent,
            StartTaskEvent,
            FinishTaskEvent,
            StartActionSubtaskEvent,
            FinishActionSubtaskEvent,
            StartStructureRunEvent,
            FinishStructureRunEvent,
            CompletionChunkEvent,
        )

        class_registry.register("StartPromptEvent", BaseSchema.from_attrscls(StartPromptEvent))
        class_registry.register("FinishPromptEvent", BaseSchema.from_attrscls(FinishPromptEvent))
        class_registry.register("StartTaskEvent", BaseSchema.from_attrscls(StartTaskEvent))
        class_registry.register("FinishTaskEvent", BaseSchema.from_attrscls(FinishTaskEvent))
        class_registry.register("StartActionSubtaskEvent", BaseSchema.from_attrscls(StartActionSubtaskEvent))
        class_registry.register("FinishActionSubtaskEvent", BaseSchema.from_attrscls(FinishActionSubtaskEvent))
        class_registry.register("StartStructureRunEvent", BaseSchema.from_attrscls(StartStructureRunEvent))
        class_registry.register("FinishStructureRunEvent", BaseSchema.from_attrscls(FinishStructureRunEvent))
        class_registry.register("CompletionChunkEvent", BaseSchema.from_attrscls(CompletionChunkEvent))

        return class_registry.get_class(obj_type)
