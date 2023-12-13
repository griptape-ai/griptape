from __future__ import annotations
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.loaders import TextLoader
from schema import Schema, Literal
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.loaders import WebLoader


@define
class WebScraper(BaseTool):
    include_links: bool = field(default=True, kw_only=True)

    @activity(
        config={
            "description": "Can be used to browse a web page and load its content",
            "schema": Schema({Literal("url", description="Valid HTTP URL"): str}),
        }
    )
    def get_content(self, params: dict) -> ListArtifact | ErrorArtifact:
        url = params["values"]["url"]
        page = WebLoader().extract_page(url, self.include_links)

        if isinstance(page, ErrorArtifact):
            return page
        else:
            return ListArtifact(TextLoader().text_to_artifacts(page.get("text")))

    @activity(
        config={
            "description": "Can be used to load a web page author",
            "schema": Schema({Literal("url", description="Valid HTTP URL"): str}),
        }
    )
    def get_author(self, params: dict) -> BaseArtifact:
        url = params["values"]["url"]
        page = WebLoader().extract_page(url, self.include_links)

        if isinstance(page, ErrorArtifact):
            return page
        else:
            return TextArtifact(page.get("author"))
