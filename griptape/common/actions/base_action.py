from abc import ABC

from griptape.mixins.serializable_mixin import SerializableMixin


class BaseAction(SerializableMixin, ABC): ...
