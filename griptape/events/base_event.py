from __future__ import annotations

import time
import uuid
from abc import ABC

from attrs import Factory, define, field

from griptape.mixins import SerializableMixin


@define
class BaseEvent(SerializableMixin, ABC):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    timestamp: float = field(default=Factory(lambda: time.time()), kw_only=True, metadata={"serializable": True})
