from __future__ import annotations

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
    bar: str | None = field(default=None, kw_only=True, metadata={"serializable": True})
    baz: list[int] | None = field(default=None, kw_only=True, metadata={"serializable": True})
    secret: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    nested: MockSerializable.NestedMockSerializable | None = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    model: BaseModel | None = field(default=None, kw_only=True, metadata={"serializable": True})
    buzz: dict[str, MockSerializable] | None = field(default=None, kw_only=True, metadata={"serializable": True})
