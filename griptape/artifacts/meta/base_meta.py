from abc import ABC
from attr import define
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseMeta(SerializableMixin, ABC):
    pass
