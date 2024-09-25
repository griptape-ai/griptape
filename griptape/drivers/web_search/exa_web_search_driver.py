from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.artifacts import JsonArtifact, ListArtifact
from griptape.drivers import BaseWebSearchDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from exa_py.api import Exa


@define
class ExaWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True)
    _client: Exa = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})

    @lazy_property()
    def client(self) -> Exa:
        return import_optional_dependency("exa_py").Exa(api_key=self.api_key)

    def search(self, query: str, **kwargs) -> ListArtifact:
        response = self.client.search_and_contents(
            query=query,
            num_results=self.results_count,
            highlights=True,
            use_autoprompt=True,
            text=True,
            **self.params,
            **kwargs,
        )
        results = [
            {"title": result.title, "url": result.url, "highlights": result.highlights, "text": result.text}
            for result in response.results
        ]
        return ListArtifact([JsonArtifact(result) for result in results])
