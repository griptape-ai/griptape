from abc import ABC, abstractmethod

from griptape.artifacts import TextArtifact


class BaseWebScraperDriver(ABC):
    def scrape_url(self, url: str) -> TextArtifact:
        source = self.fetch_url(url)

        return self.extract_page(source)

    @abstractmethod
    def fetch_url(self, url: str) -> str: ...

    @abstractmethod
    def extract_page(self, page: str) -> TextArtifact: ...
