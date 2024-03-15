import json
import logging
from typing import Optional
from attr import define, field
from griptape.drivers import BaseWebScraperDriver
from griptape.utils import import_optional_dependency


@define
class TrafilaturaWebScraperDriver(BaseWebScraperDriver):
    include_links: bool = field(default=True, kw_only=True)

    def scrape_url(self, url: str, *args, **kwargs) -> str:
        trafilatura = import_optional_dependency("trafilatura")
        use_config = trafilatura.settings.use_config

        config = use_config()
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
            extracted_page = trafilatura.extract(
                page, include_links=self.include_links, output_format="json", config=config
            )

            if extracted_page:
                return json.loads(extracted_page).get("text")
            else:
                raise Exception("can't extract page")
