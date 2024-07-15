from __future__ import annotations

import json

import requests
from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseWebSearchDriver


@define
class GoogleWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(default=None, kw_only=True)
    search_id: str = field(default=None, kw_only=True)

    def search(self, query: str, **kwargs) -> ListArtifact:
        return ListArtifact([TextArtifact(json.dumps(result)) for result in self._search_google(query, **kwargs)])

    def _search_google(self, query: str, **kwargs) -> list[dict]:
        url = (
            f"https://www.googleapis.com/customsearch/v1?"
            f"key={self.api_key}&"
            f"cx={self.search_id}&"
            f"q={query}&"
            f"start=0&"
            f"lr=lang_{self.language}&"
            f"num={self.results_count}&"
            f"gl={self.country}"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            links = [{"url": r["link"], "title": r["title"], "description": r["snippet"]} for r in data["items"]]

            return links
        else:
            raise Exception(
                f"Google Search API returned an error with status code "
                f"{response.status_code} and reason '{response.reason}'",
            )
