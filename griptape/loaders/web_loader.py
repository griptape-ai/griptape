from __future__ import annotations

from typing import Any, cast

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver, TrafilaturaWebScraperDriver
from griptape.loaders import BaseLoader


@define
class WebLoader(BaseLoader):
    web_scraper_driver: BaseWebScraperDriver = field(
        default=Factory(lambda: TrafilaturaWebScraperDriver()),
        kw_only=True,
    )

    def load(self, source: Any, *args, **kwargs) -> TextArtifact:
        return cast(TextArtifact, super().load(source, *args, **kwargs))

    def fetch(self, source: str, *args, **kwargs) -> str:
        return self.web_scraper_driver.fetch_url(source)

    def parse(self, source: str, *args, **kwargs) -> TextArtifact:
        return self.web_scraper_driver.extract_page(source)
