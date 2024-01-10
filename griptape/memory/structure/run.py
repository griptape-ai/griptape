import uuid
from attr import define, field, Factory
from griptape.mixins import SerializableMixin


@define
class Run(SerializableMixin):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serialize": True})
    input: str = field(kw_only=True, metadata={"serialize": True})
    output: str = field(kw_only=True, metadata={"serialize": True})
