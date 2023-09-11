import json
import logging
from attr import define
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.loaders import TextLoader
import trafilatura
from trafilatura.settings import use_config


@define
class WebLoader(TextLoader):
    def load(self, url: str, include_links: bool = True) -> list[TextArtifact]:
        return self._load_page(url, include_links)

    def load_collection(self, urls: list[str], include_links: bool = True) -> dict[str, list[TextArtifact]]:
        return utils.execute_futures_dict({
            utils.str_to_hash(u): self.futures_executor.submit(self._load_page, u, include_links)
            for u in urls
        })

    def _load_page(self, url: str, include_links: bool = True) -> list[TextArtifact]:
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
            result = json.loads(
                trafilatura.extract(
                    page,
                    include_links=include_links,
                    output_format="json",
                    config=config
                )
            )

            return self.text_to_artifacts(result.get("text"))
