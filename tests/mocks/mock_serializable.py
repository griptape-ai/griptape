from attrs import define, field
from typing import Optional
from griptape.mixins import SerializableMixin


@define
class MockSerializable(SerializableMixin):
    foo: str = field(default="bar", kw_only=True, metadata={"serializable": True})
    bar: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    baz: Optional[list[int]] = field(default=None, kw_only=True, metadata={"serializable": True})
