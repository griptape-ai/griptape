from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.utils import with_contextvars
from griptape.utils.futures import execute_futures_dict
from griptape.utils.hash import bytes_to_hash, str_to_hash

if TYPE_CHECKING:
    from collections.abc import Mapping

    from griptape.common import Reference

S = TypeVar("S")  # Type for the input source
F = TypeVar("F")  # Type for the fetched data
A = TypeVar("A", bound=BaseArtifact)  # Type for the returned Artifact


@define
class BaseLoader(FuturesExecutorMixin, ABC, Generic[S, F, A]):
    """Fetches data from a source, parses it, and returns an Artifact.

    Attributes:
        reference: The optional `Reference` to set on the Artifact.
    """

    reference: Optional[Reference] = field(default=None, kw_only=True)

    def load(self, source: S) -> A:
        data = self.fetch(source)

        return self.parse(data)

    @abstractmethod
    def fetch(self, source: S) -> F:
        """Fetches data from the source."""

    ...

    def parse(self, data: F) -> A:
        """Parses the fetched data and returns an Artifact."""
        artifact = self.try_parse(data)

        artifact.reference = self.reference

        return artifact

    def try_parse(self, data: F) -> A:
        """Parses the fetched data and returns an Artifact."""
        # TODO: Mark as abstract method for griptape 2.0
        raise NotImplementedError()

    def load_collection(
        self,
        sources: list[Any],
    ) -> Mapping[str, A]:
        """Loads a collection of sources and returns a dictionary of Artifacts."""
        # Create a dictionary before actually submitting the jobs to the executor
        # to avoid duplicate work.
        sources_by_key = {self.to_key(source): source for source in sources}

        with self.create_futures_executor() as futures_executor:
            return execute_futures_dict(
                {
                    key: futures_executor.submit(with_contextvars(self.load), source)
                    for key, source in sources_by_key.items()
                },
            )

    def to_key(self, source: S) -> str:
        """Converts the source to a key for the collection."""
        if isinstance(source, bytes):
            return bytes_to_hash(source)
        else:
            return str_to_hash(str(source))
