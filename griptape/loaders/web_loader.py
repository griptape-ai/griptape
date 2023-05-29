import json
import logging
from typing import Union
from attr import define
from griptape.artifacts import ListArtifact, ErrorArtifact
from griptape.loaders import TextLoader
import trafilatura
from trafilatura.settings import use_config


@define
class WebLoader(TextLoader):
    def load(self, url: str, include_links: bool = True) -> Union[ListArtifact, ErrorArtifact]:
        page = self._load_page(url, include_links)

        if isinstance(page, ErrorArtifact):
            return page
        else:
            return self.text_to_artifact(page.get("text"))

    def _load_page(self, url: str, include_links: bool = True) -> Union[dict, ErrorArtifact]:
        config = trafilatura.settings.use_config()
        page = trafilatura.fetch_url(url)

        # This disables signal, so that trafilatura can work on any thread:
        # More info: https://trafilatura.readthedocs.io/en/latest/usage-python.html#disabling-signal
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

        # Disable error logging in trafilatura as it sometimes logs errors from lxml, even though
        # the end result of page parsing is successful.
        logging.getLogger("trafilatura").setLevel(logging.FATAL)

        if page is None:
            return ErrorArtifact("error: can't access URL")
        else:
            return json.loads(
                trafilatura.extract(
                    page,
                    include_links=include_links,
                    output_format="json",
                    config=config
                )
            )
