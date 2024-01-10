from __future__ import annotations
import json
from attr import define
from abc import ABC

from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError


@define
class BaseMetaEntry(SerializableMixin, ABC):
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> BaseMetaEntry:
        from griptape.memory.meta import ActionSubtaskMetaEntry

        class_registry.register("ConversationMemory", BaseSchema.from_attrscls(ActionSubtaskMetaEntry))

        try:
            return class_registry.get_class(data["type"])().load(data)
        except RegistryError:
            raise ValueError("Unsupported memory type")
