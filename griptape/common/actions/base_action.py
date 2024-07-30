from abc import ABC

from griptape.mixins import SerializableMixin


class BaseAction(SerializableMixin, ABC): ...
