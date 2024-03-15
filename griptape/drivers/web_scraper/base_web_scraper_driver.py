from abc import ABC, abstractmethod
from typing import Optional


class BaseWebScraperDriver(ABC):
    @abstractmethod
    def scrape_url(self, url: str, *args, **kwargs) -> str:
        ...
