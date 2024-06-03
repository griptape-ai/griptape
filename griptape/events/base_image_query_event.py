from abc import ABC

from attrs import define

from griptape.events import BaseEvent


@define
class BaseImageQueryEvent(BaseEvent, ABC): ...
