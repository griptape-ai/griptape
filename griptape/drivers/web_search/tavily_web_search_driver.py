from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
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
    params: dict = field(default=Factory(dict), kw_only=True, metadata={"serializable": True})

    def search(self, query: str, **kwargs) -> ListArtifact:
        response = self.client.search(query, max_results=self.results_count, **self.params, **kwargs)
        results = response["results"]
        return ListArtifact(
            [
                TextArtifact(json.dumps({"title": result["title"], "url": result["url"], "content": result["content"]}))
                for result in results
            ]
        )
