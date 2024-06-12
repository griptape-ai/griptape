from __future__ import annotations
from attrs import define, field, Factory
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.drivers import BaseWebScraperDriver, TrafilaturaWebScraperDriver
from griptape.artifacts import TextArtifact
from griptape.loaders import BaseTextLoader


@define
class WebLoader(BaseTextLoader):
    web_scraper_driver: BaseWebScraperDriver = field(
        default=Factory(lambda: TrafilaturaWebScraperDriver()), kw_only=True
    )

    def load(self, source: str, *args, **kwargs) -> ErrorArtifact | list[TextArtifact]:
        try:
            single_chunk_text_artifact = self.web_scraper_driver.scrape_url(source)
            return self._text_to_artifacts(single_chunk_text_artifact.value)
        except Exception as e:
            return ErrorArtifact(f"Error loading from source: {source}", exception=e)
