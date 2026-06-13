from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.artifacts import JsonArtifact, ListArtifact
from griptape.drivers.web_search import BaseWebSearchDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property
from griptape.utils.deprecation import deprecation_warn

if TYPE_CHECKING:
    from exa_py.api import Exa


@define
class ExaWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True, default=None)
    highlights: bool = field(default=False, kw_only=True)
    use_autoprompt: bool = field(default=False, kw_only=True)
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    _client: Exa | None = field(default=None, kw_only=True, alias="client")

    def __attrs_post_init__(self) -> None:
        if self.use_autoprompt:
            deprecation_warn(
                "`use_autoprompt` is deprecated and no longer sent to the Exa API, which removed support for it. "
                "The Exa API now handles query optimization automatically. This parameter will be removed in a "
                "future release."
            )

    @lazy_property()
    def client(self) -> Exa:
        return import_optional_dependency("exa_py").Exa(api_key=self.api_key)

    def search(self, query: str, **kwargs) -> ListArtifact[JsonArtifact]:
        response = self.client.search_and_contents(  # pyright: ignore[reportCallIssue]
            highlights=self.highlights,  # pyright: ignore[reportArgumentType]
            query=query,
            num_results=self.results_count,
            text=True,
            **self.params,
            **kwargs,
        )
        results = [
            {"title": result.title, "url": result.url, "highlights": result.highlights, "text": result.text}
            for result in response.results
        ]
        return ListArtifact([JsonArtifact(result) for result in results])
