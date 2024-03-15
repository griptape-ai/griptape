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

    def load(self, source: str, include_links: bool = True, *args, **kwargs) -> list[TextArtifact]:
        return self._load_page_to_artifacts(source, include_links)

    def load_collection(
        self, sources: list[str], include_links: bool = True, *args, **kwargs
    ) -> dict[str, list[TextArtifact]]:
        return execute_futures_dict(
            {
                str_to_hash(source): self.futures_executor.submit(self._load_page_to_artifacts, source, include_links)
                for source in sources
            }
        )

    def _load_page_to_artifacts(self, url: str, include_links: bool = True) -> list[TextArtifact]:
        page_text = self.extract_page(url, include_links)

        if page_text is None:
            return []

        return self._text_to_artifacts(page_text)

    def extract_page(self, url: str, include_links: bool = True) -> str:
        return self.web_scraper_driver.scrape_url(url, include_links)
