from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.artifacts import JsonArtifact, ListArtifact
from griptape.drivers.web_search import BaseWebSearchDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from firecrawl import Firecrawl


@define
class FirecrawlWebSearchDriver(BaseWebSearchDriver):
    """Web Search Driver for the Firecrawl Search API.

    Returns web results with their title, url and description. When `scrape_options` is set in `params`,
    each result also carries the requested page content (markdown, summary or json).

    Attributes:
        api_key: Firecrawl API key.
        api_url: Firecrawl API base URL. Override it to use a self-hosted Firecrawl instance.
        params: Extra keyword arguments passed to `Firecrawl.search` on every call,
            for example `{"tbs": "qdr:w"}` or `{"scrape_options": {"formats": ["markdown"]}}`.
    """

    api_key: str = field(kw_only=True)
    api_url: str = field(default="https://api.firecrawl.dev", kw_only=True, metadata={"serializable": True})
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    _client: Firecrawl | None = field(default=None, kw_only=True, alias="client")

    @lazy_property()
    def client(self) -> Firecrawl:
        return import_optional_dependency("firecrawl").Firecrawl(
            api_key=self.api_key, api_url=self.api_url, origin="griptape"
        )

    def search(self, query: str, **kwargs) -> ListArtifact[JsonArtifact]:
        response = self.client.search(query, limit=self.results_count, **self.params, **kwargs)
        results = [self._to_dict(result) for result in response.web or []]
        return ListArtifact([JsonArtifact(result) for result in results])

    def _to_dict(self, result: Any) -> dict:
        if not isinstance(result, import_optional_dependency("firecrawl.types").Document):
            return {"title": result.title, "url": result.url, "description": result.description}

        # With scrape_options set, results come back as scraped Documents that keep title and url in their metadata.
        metadata = result.metadata_typed
        return {
            "title": metadata.title,
            "url": metadata.url or metadata.source_url,
            "description": metadata.description,
            **{key: value for key in ("markdown", "summary", "json") if (value := getattr(result, key)) is not None},
        }
