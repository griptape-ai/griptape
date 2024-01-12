from __future__ import annotations
from attr import define
from abc import ABC

from griptape.mixins import SerializableMixin
from griptape.schemas import BaseSchema
from marshmallow import class_registry
from marshmallow.schema import Schema


@define
class BaseMetaEntry(SerializableMixin, ABC):
    @classmethod
    def try_get_schema(cls, obj_type: str) -> list[type[Schema]] | type[Schema]:
        from griptape.memory.meta import ActionSubtaskMetaEntry

        class_registry.register("ActionSubtaskMetaEntry", BaseSchema.from_attrs_cls(ActionSubtaskMetaEntry))

        return class_registry.get_class(obj_type)
