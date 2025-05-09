from __future__ import annotations

from typing import Callable

import requests
from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers.web_scraper import BaseWebScraperDriver


@define
class ProxyWebScraperDriver(BaseWebScraperDriver):
    proxies: dict = field(kw_only=True, metadata={"serializable": False})
    params: dict = field(default=Factory(dict), kw_only=True, metadata={"serializable": True})
    _extract_page: Callable[[ProxyWebScraperDriver, str], TextArtifact] = field(
        default=Factory(lambda: lambda _, page: TextArtifact(page)),
        kw_only=True,
        alias="extract_page",
        metadata={"serializable": False},
    )

    def fetch_url(self, url: str) -> str:
        response = requests.get(url, proxies=self.proxies, **self.params)

        return response.text

    def extract_page(self, page: str) -> TextArtifact:
        return self._extract_page(self, page)
