from abc import ABC
from attr import define, field
from griptape.executors import BaseExecutor, LocalExecutor


@define
class BaseConverter(ABC):
    executor: BaseExecutor = field(default=LocalExecutor(), kw_only=True)
