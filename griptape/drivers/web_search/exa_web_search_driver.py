from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseWebSearchDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from exa_py.api import Exa


@define
class ExaWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True)
    client: Exa = field(
        default=Factory(lambda self: import_optional_dependency("exa_py.api").Exa(self.api_key), takes_self=True),
        kw_only=True,
    )

    def search(self, query: str, **kwargs) -> ListArtifact:
        try:
            results = self.client.search(query, num_results=self.results_count, **kwargs)
            return ListArtifact(
                [
                    TextArtifact(
                        json.dumps({"title": result.title, "url": result.url, "description": result.author}),
                    )
                    for result in results.results
                ],
            )
        except Exception as e:
            raise Exception(f"Error searching '{query}' with Exa: {e}") from e
