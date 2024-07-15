from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseWebSearchDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from duckduckgo_search import DDGS


@define
class DuckDuckGoWebSearchDriver(BaseWebSearchDriver):
    client: DDGS = field(default=Factory(lambda: import_optional_dependency("duckduckgo_search").DDGS()), kw_only=True)

    def search(self, query: str, **kwargs) -> ListArtifact:
        try:
            results = self.client.text(query, region=f"{self.language}-{self.country}", max_results=self.results_count)
            return ListArtifact(
                [
                    TextArtifact(
                        json.dumps({"title": result["title"], "url": result["href"], "description": result["body"]}),
                    )
                    for result in results
                ],
            )
        except Exception as e:
            raise Exception(f"Error searching '{query}' with DuckDuckGo: {e}") from e
