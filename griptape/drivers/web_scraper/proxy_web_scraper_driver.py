from __future__ import annotations

from attrs import field, Factory, define
import requests

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver


@define
class ProxyWebScraperDriver(BaseWebScraperDriver):
    proxies: dict = field(kw_only=True, metadata={"serializable": False})
    params: dict = field(default=Factory(dict), kw_only=True, metadata={"serializable": True})

    def scrape_url(self, url: str) -> TextArtifact:
        response = requests.get(url, proxies=self.proxies, **self.params)
        return TextArtifact(response.text)
