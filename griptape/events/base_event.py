from attr import define, field, Factory
from typing import Union
from dataclasses import dataclass


@define
class BaseEvent:
    @dataclass
    class BaseEventType:
        pass

    @dataclass
    class StartTaskEventType(BaseEventType):
        pass

    @dataclass
    class FinishTaskEventType(BaseEventType):
        pass

    @dataclass
    class StartSubtaskEventType(BaseEventType):
        pass

    @dataclass
    class FinishSubtaskEventType(BaseEventType):
        pass

    event_type: Union[
        StartTaskEventType, FinishTaskEventType, StartSubtaskEventType, FinishSubtaskEventType
    ] = field(kw_only=True)
    data: bytes = field(default=None, kw_only=True)
