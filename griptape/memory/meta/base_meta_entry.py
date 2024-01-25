from __future__ import annotations
from attr import define
from abc import ABC

from griptape.mixins import SerializableMixin


@define
class BaseMetaEntry(SerializableMixin, ABC):
    ...
