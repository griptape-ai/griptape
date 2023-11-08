from __future__ import annotations
from attr import define, field
from griptape.artifacts import TextArtifact, ErrorArtifact, ListArtifact
from schema import Schema, Literal
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
import requests


@define
class WebSearch(BaseTool):
    results_count: int = field(default=5, kw_only=True)
    google_api_lang: str = field(default="lang_en", kw_only=True)
    google_api_key: str = field(kw_only=True)
    google_api_search_id: str = field(kw_only=True)
    google_api_country: str = field(default="us", kw_only=True)

    @activity(
        config={
            "description": "Can be used for searching the web",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="Search engine request that returns a list of pages with titles, descriptions, and URLs",
                    ): str
                }
            ),
        }
    )
    def search(self, props: dict) -> ListArtifact | ErrorArtifact:
        query = props["values"]["query"]

        try:
            return ListArtifact([TextArtifact(str(result)) for result in self._search_google(query)])
        except Exception as e:
            return ErrorArtifact(f"error searching Google: {e}")

    def _search_google(self, query: str) -> list[dict]:
        url = (
            f"https://www.googleapis.com/customsearch/v1?"
            f"key={self.google_api_key}&"
            f"cx={self.google_api_search_id}&"
            f"q={query}&"
            f"start=0&"
            f"lr={self.google_api_lang}&"
            f"num={self.results_count}&"
            f"gl={self.google_api_country}"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            links = [{"url": r["link"], "title": r["title"], "description": r["snippet"]} for r in data["items"]]

            return links
        else:
            raise Exception(
                f"Google Search API returned an error with status code "
                f"{response.status_code} and reason '{response.reason}'"
            )
