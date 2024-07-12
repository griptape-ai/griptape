from __future__ import annotations

from abc import ABC

from attrs import define

from griptape.mixins import SerializableMixin


@define
class BaseMetaEntry(SerializableMixin, ABC): ...
