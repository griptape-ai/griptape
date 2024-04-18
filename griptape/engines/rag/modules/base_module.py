from abc import ABC
from concurrent import futures
from attr import define, field, Factory


@define(kw_only=True)
class BaseModule(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()))
