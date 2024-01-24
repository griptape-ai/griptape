from attrs import define
from abc import ABC

from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseConfig(SerializableMixin, ABC):
    ...
