from __future__ import annotations

import json

import requests
from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseWebSearchDriver


@define
class GoogleWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True)
    search_id: str = field(kw_only=True)
    language: str = field(default="en", kw_only=True)
    country: str = field(default="us", kw_only=True)

    def search(self, query: str, **kwargs) -> ListArtifact:
        return ListArtifact([TextArtifact(json.dumps(result)) for result in self._search_google(query, **kwargs)])

    def _search_google(self, query: str, **kwargs) -> list[dict]:
        query_params = {
            "key": self.api_key,
            "cx": self.search_id,
            "q": query,
            "start": 0,
            "lr": f"lang_{self.language}",
            "num": self.results_count,
            "gl": self.country,
            **kwargs,
        }
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=query_params)

        if response.status_code == 200:
            data = response.json()

            return [{"url": r["link"], "title": r["title"], "description": r["snippet"]} for r in data["items"]]

        else:
            raise Exception(
                f"Google Search API returned an error with status code "
                f"{response.status_code} and reason '{response.reason}'",
            )
