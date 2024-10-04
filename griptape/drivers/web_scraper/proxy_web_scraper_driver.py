from __future__ import annotations

import requests
from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver


@define
class ProxyWebScraperDriver(BaseWebScraperDriver):
    proxies: dict = field(kw_only=True, metadata={"serializable": False})
    params: dict = field(default=Factory(dict), kw_only=True, metadata={"serializable": True})

    def fetch_url(self, url: str) -> str:
        response = requests.get(url, proxies=self.proxies, **self.params)

        return response.text

    def extract_page(self, page: str) -> TextArtifact:
        return TextArtifact(page)
