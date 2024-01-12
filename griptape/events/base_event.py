from __future__ import annotations
import time
from abc import ABC
from marshmallow import Schema, class_registry
from attr import define, field, Factory

from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema


@define
class BaseEvent(SerializableMixin, ABC):
    timestamp: float = field(default=Factory(lambda: time.time()), kw_only=True, metadata={"serializable": True})

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

        class_registry.register("StartPromptEvent", BaseSchema.from_attrs_cls(StartPromptEvent))
        class_registry.register("FinishPromptEvent", BaseSchema.from_attrs_cls(FinishPromptEvent))
        class_registry.register("StartTaskEvent", BaseSchema.from_attrs_cls(StartTaskEvent))
        class_registry.register("FinishTaskEvent", BaseSchema.from_attrs_cls(FinishTaskEvent))
        class_registry.register("StartActionSubtaskEvent", BaseSchema.from_attrs_cls(StartActionSubtaskEvent))
        class_registry.register("FinishActionSubtaskEvent", BaseSchema.from_attrs_cls(FinishActionSubtaskEvent))
        class_registry.register("StartStructureRunEvent", BaseSchema.from_attrs_cls(StartStructureRunEvent))
        class_registry.register("FinishStructureRunEvent", BaseSchema.from_attrs_cls(FinishStructureRunEvent))
        class_registry.register("CompletionChunkEvent", BaseSchema.from_attrs_cls(CompletionChunkEvent))

        return class_registry.get_class(obj_type)
