from __future__ import annotations

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver, TrafilaturaWebScraperDriver
from griptape.loaders import BaseLoader


@define
class WebLoader(BaseLoader[str, str, TextArtifact]):
    web_scraper_driver: BaseWebScraperDriver = field(
        default=Factory(lambda: TrafilaturaWebScraperDriver()),
        kw_only=True,
    )

    def fetch(self, source: str) -> str:
        return self.web_scraper_driver.fetch_url(source)

    def try_parse(self, data: str) -> TextArtifact:
        return self.web_scraper_driver.extract_page(data)
