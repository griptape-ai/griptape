from abc import ABC, abstractmethod

from griptape.artifacts import TextArtifact


class BaseWebScraperDriver(ABC):
    @abstractmethod
    def scrape_url(self, url: str) -> TextArtifact: ...
