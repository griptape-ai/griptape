from __future__ import annotations

import json
from typing import TypeVar, Generic

from attr import Factory, define, field

from griptape.schemas.base_schema import BaseSchema

T = TypeVar("T", bound="SerializableMixin")


@define(slots=False)
class SerializableMixin(Generic[T]):
    type: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serialize": True},
    )

    @classmethod
    def before_load(cls: type[T], data: dict) -> dict:
        return data

    @classmethod
    def before_dump(cls: type[T], data: T) -> T:
        return data

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        schema = BaseSchema.from_attrscls(cls)

        return schema().load(data)

    @classmethod
    def from_json(cls: type[T], data: str) -> T:
        return cls.from_dict(json.loads(data))

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        schema = BaseSchema.from_attrscls(self.__class__)

        return dict(schema().dump(self))
