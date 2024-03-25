from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseWebScraperDriver, TrafilaturaWebScraperDriver
from griptape.utils import str_to_hash, execute_futures_dict
from griptape.artifacts import TextArtifact
from griptape.loaders import BaseTextLoader


@define
class WebLoader(BaseTextLoader):
    web_scraper_driver: BaseWebScraperDriver = field(
        default=Factory(lambda: TrafilaturaWebScraperDriver()), kw_only=True
    )

    def load(self, source: str, *args, **kwargs) -> list[TextArtifact]:
        return self._load_page_to_artifacts(source)

    def load_collection(self, sources: list[str], *args, **kwargs) -> dict[str, list[TextArtifact]]:
        return execute_futures_dict(
            {
                str_to_hash(source): self.futures_executor.submit(self._load_page_to_artifacts, source)
                for source in sources
            }
        )

    def _load_page_to_artifacts(self, url: str) -> list[TextArtifact]:
        single_chunk_text_artifact = self.extract_page(url)
        return self._text_to_artifacts(single_chunk_text_artifact.value)

    def extract_page(self, url: str) -> TextArtifact:
        return self.web_scraper_driver.scrape_url(url)
