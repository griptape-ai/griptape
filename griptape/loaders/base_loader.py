from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from attrs import define, field

from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.utils.futures import execute_futures_dict
from griptape.utils.hash import bytes_to_hash, str_to_hash

if TYPE_CHECKING:
    from collections.abc import Mapping

    from griptape.common import Reference

S = TypeVar("S")
F = TypeVar("F")
A = TypeVar("A", bound=BaseArtifact)


@define
class BaseLoader(FuturesExecutorMixin, ABC, Generic[S, F, A]):
    reference: Optional[Reference] = field(default=None, kw_only=True)

    def load(self, source: S, *args, **kwargs) -> A:
        data = self.fetch(source)

        artifact = self.parse(data)

        artifact.reference = self.reference

        return artifact

    @abstractmethod
    def fetch(self, source: S) -> F: ...

    @abstractmethod
    def parse(self, source: F) -> A: ...

    def load_collection(
        self,
        sources: list[Any],
        *args,
        **kwargs,
    ) -> Mapping[str, A]:
        # Create a dictionary before actually submitting the jobs to the executor
        # to avoid duplicate work.
        sources_by_key = {self.to_key(source): source for source in sources}

        return execute_futures_dict(
            {
                key: self.futures_executor.submit(self.load, source, *args, **kwargs)
                for key, source in sources_by_key.items()
            },
        )

    def to_key(self, source: Any) -> str:
        if isinstance(source, bytes):
            return bytes_to_hash(source)
        else:
            return str_to_hash(str(source))
