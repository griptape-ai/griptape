import json
import math
from typing import Optional
import requests
import stopit
from attrs import define, field
from warpspeed.tools import Tool
from googlesearch import search as google_search


@define
class GoogleSearchTool(Tool):
    results_count: int = field(default=5, kw_only=True)
    lang: str = field(default="en", kw_only=True)
    timeout: int = field(default=10, kw_only=True)

    use_api: bool = field(default=False, kw_only=True)
    api_search_key: Optional[str] = field(default=None, kw_only=True)
    api_search_id: Optional[str] = field(default=None, kw_only=True)
    api_country: str = field(default="us", kw_only=True)

    def run(self, query: str) -> str:
        try:
            return self.gsearch_wrapper(query, timeout=self.timeout)
        except Exception as e:
            return f"error searching Google: {e}"

    @stopit.threading_timeoutable(default="Google search timed out")
    def gsearch_wrapper(self, query: str) -> str:
        if self.use_api:
            results_list = self.search_api(query)
        else:
            results_list = self.scrape(query)

        return json.dumps(results_list)

    def scrape(self, query: str) -> list[dict]:
        raw_results = list(google_search(query, self.results_count, self.lang, advanced=True))

        return [{
            "url": r.url,
            "title": r.title,
            "description": r.description
        } for r in raw_results]

    def search_api(self, query: str) -> list[dict]:
        url = f"https://www.googleapis.com/customsearch/v1?" \
              f"key={self.api_search_key}&" \
              f"cx={self.api_search_id}&" \
              f"q={query}&" \
              f"start=0&" \
              f"num={self.results_count}&" \
              f"gl={self.api_country}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            links = [{
                "url": r["link"],
                "title": r["title"],
                "description": r["snippet"],
            } for r in data["items"]]

            return links
        else:
            raise Exception(f"Google Search API returned an error with status code "
                            f"{response.status_code} and reason '{response.reason}'")
