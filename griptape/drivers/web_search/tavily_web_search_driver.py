from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field
from tavily import BadRequestError

from griptape.artifacts import JsonArtifact, ListArtifact
from griptape.drivers import BaseWebSearchDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from tavily import TavilyClient


@define
class TavilyWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True)
    client: TavilyClient = field(
        default=Factory(lambda self: import_optional_dependency("tavily").TavilyClient(self.api_key), takes_self=True),
        kw_only=True,
    )
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})

    def search(self, query: str, **kwargs) -> ListArtifact:
        response = self.client.search(query, max_results=self.results_count, **self.params, **kwargs)
        results = response.get("results", [])
        if not results:
            raise BadRequestError("No results found or the response structure is invalid.")
        return ListArtifact([(JsonArtifact(result)) for result in results])
