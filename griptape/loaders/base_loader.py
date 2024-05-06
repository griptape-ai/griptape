from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent import futures
from typing import Any, Optional
from collections.abc import Mapping, Sequence

from attr import define, field, Factory

from griptape.artifacts import BaseArtifact
from griptape.utils.futures import execute_futures_dict
from griptape.utils.hash import bytes_to_hash, str_to_hash


@define
class BaseLoader(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)
    encoding: Optional[str] = field(default=None, kw_only=True)

    @abstractmethod
    def load(self, source: Any, *args, **kwargs) -> BaseArtifact | Sequence[BaseArtifact]:
        ...

    def load_collection(
        self, sources: list[Any], *args, **kwargs
    ) -> Mapping[str, BaseArtifact | Sequence[BaseArtifact | Sequence[BaseArtifact]]]:
        # Create a dictionary before actually submitting the jobs to the executor
        # to avoid duplicate work.
        sources_by_key = {self.to_key(source): source for source in sources}
        return execute_futures_dict(
            {
                key: self.futures_executor.submit(self.load, source, *args, **kwargs)
                for key, source in sources_by_key.items()
            }
        )

    def to_key(self, source: Any, *args, **kwargs) -> str:
        if isinstance(source, bytes):
            return bytes_to_hash(source)
        elif isinstance(source, str):
            return str_to_hash(source)
        else:
            return str_to_hash(str(source))
