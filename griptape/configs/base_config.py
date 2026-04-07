from __future__ import annotations

from abc import ABC

from attrs import define

from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class BaseConfig(SerializableMixin, ABC): ...
