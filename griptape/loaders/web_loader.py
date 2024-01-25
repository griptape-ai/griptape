import json
import logging
from attr import define

import trafilatura

from griptape.utils import str_to_hash, execute_futures_dict
from griptape.artifacts import TextArtifact
from griptape.loaders import TextLoader


@define
class WebLoader(TextLoader):
    def load(self, source: str, include_links: bool = True, *args, **kwargs) -> list[TextArtifact]:
        return self._load_page_to_artifacts(source, include_links)

    def load_collection(self, sources: list[str], include_links: bool = True, *args, **kwargs) -> dict[str, list[TextArtifact]]:
        return execute_futures_dict(
            {str_to_hash(source): self.futures_executor.submit(self._load_page_to_artifacts, source, include_links) for source in sources}
        )

    def _load_page_to_artifacts(self, url: str, include_links: bool = True) -> list[TextArtifact]:
        return self.text_to_artifacts(self.extract_page(url, include_links).get("text"))

    def extract_page(self, url: str, include_links: bool = True) -> dict:
        config = trafilatura.settings.use_config()
        page = trafilatura.fetch_url(url, no_ssl=True)

        # This disables signal, so that trafilatura can work on any thread:
        # More info: https://trafilatura.readthedocs.io/usage-python.html#disabling-signal
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

        # Disable error logging in trafilatura as it sometimes logs errors from lxml, even though
        # the end result of page parsing is successful.
        logging.getLogger("trafilatura").setLevel(logging.FATAL)

        if page is None:
            raise Exception("can't access URL")
        else:
            extracted_page = trafilatura.extract(page, include_links=include_links, output_format="json", config=config)
            if extracted_page:
                return json.loads(extracted_page)
            else:
                raise Exception("can't extract page")
