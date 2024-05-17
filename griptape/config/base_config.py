from abc import ABC

from attrs import define

from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseConfig(SerializableMixin, ABC): ...
