from __future__ import annotations
import time
from abc import ABC
from attr import define, field, Factory

from griptape.mixins import SerializableMixin


@define
class BaseEvent(SerializableMixin, ABC):
    timestamp: float = field(default=Factory(lambda: time.time()), kw_only=True, metadata={"serializable": True})
