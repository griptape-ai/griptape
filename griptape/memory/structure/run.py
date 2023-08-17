import uuid
from attr import define, field, Factory


@define
class Run:
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    input: str = field(kw_only=True)
    output: str = field(kw_only=True)
