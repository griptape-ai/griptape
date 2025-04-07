from __future__ import annotations

from typing import Optional

from attrs import define, field
from pydantic import BaseModel

from griptape.mixins.serializable_mixin import SerializableMixin


@define
class MockSerializable(SerializableMixin):
    @define
    class NestedMockSerializable(SerializableMixin):
        foo: str = field(default="bar", kw_only=True, metadata={"serializable": True})

    class MockOutput(BaseModel):
        foo: str

    foo: str = field(default="bar", kw_only=True, metadata={"serializable": True})
    bar: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    baz: Optional[list[int]] = field(default=None, kw_only=True, metadata={"serializable": True})
    secret: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    nested: Optional[MockSerializable.NestedMockSerializable] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    model: Optional[BaseModel] = field(default=None, kw_only=True, metadata={"serializable": True})
    buzz: Optional[dict[str, MockSerializable]] = field(default=None, kw_only=True, metadata={"serializable": True})
