from abc import ABC

from attr import define

from griptape.events import BaseEvent


@define
class BaseImageQueryEvent(BaseEvent, ABC):
    ...
