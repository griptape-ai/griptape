from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field
from tavily import InvalidAPIKeyError, MissingAPIKeyError, UsageLimitExceededError

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

    def search(self, query: str, **kwargs) -> ListArtifact:
        try:
            response = self.client.search(query, max_results=self.results_count, **kwargs)
            results = response["results"]
            return ListArtifact(
                [
                    TextArtifact(
                        json.dumps({"title": result["title"], "url": result["url"], "content": result["content"]})
                    )
                    for result in results
                ]
            )
        except MissingAPIKeyError as exc:
            raise ValueError("API Key is missing, Please provide a valid Tavily API Key.") from exc
        except UsageLimitExceededError as exc:
            raise ValueError("Usage Limit Exceeded, Please try again later.") from exc
        except InvalidAPIKeyError as exc:
            raise ValueError("Invalid API Key, Please provide a valid Tavily API Key.") from exc
        except Exception as e:
            raise ValueError(f"An error occurred while searching for {query} using Tavily: {e}") from e
