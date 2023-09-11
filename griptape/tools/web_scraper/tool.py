from __future__ import annotations
import logging
import json
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.loaders import TextLoader
from schema import Schema, Literal
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class WebScraper(BaseTool):
    include_links: bool = field(default=True, kw_only=True)

    @activity(config={
        "description": "Can be used to browse a web page and load its content",
        "schema": Schema({
            Literal(
                "url",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_content(self, params: dict) -> ListArtifact | ErrorArtifact:
        url = params["values"]["url"]
        page = self._load_page(url)

        if isinstance(page, ErrorArtifact):
            return page
        else:
            return ListArtifact(
                TextLoader().text_to_artifacts(page.get("text"))
            )

    @activity(config={
        "description": "Can be used to load a web page author",
        "schema": Schema({
            Literal(
                "url",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_author(self, params: dict) -> BaseArtifact:
        url = params["values"]["url"]
        page = self._load_page(url)

        if isinstance(page, ErrorArtifact):
            return page
        else:
            return TextArtifact(page.get("author"))

    def _load_page(self, url: str) -> dict | ErrorArtifact:
        import trafilatura
        from trafilatura.settings import use_config

        config = use_config()
        page = trafilatura.fetch_url(url, no_ssl=True)

        # This disables signal, so that trafilatura can work on any thread:
        # More info: https://trafilatura.readthedocs.io/usage-python.html#disabling-signal
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

        # Disable error logging in trafilatura as it sometimes logs errors from lxml, even though
        # the end result of page parsing is successful.
        logging.getLogger("trafilatura").setLevel(logging.FATAL)

        if page is None:
            return ErrorArtifact("error: can't access URL")
        else:
            content = trafilatura.extract(
                    page,
                    include_links=self.include_links,
                    output_format="json",
                    config=config
                )

            if content:
                return json.loads(content)
            else:
                return ErrorArtifact("error: can't load web page content")
