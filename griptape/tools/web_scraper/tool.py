from __future__ import annotations

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.chunkers import TextChunker
from griptape.loaders import WebLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class WebScraperTool(BaseTool):
    web_loader: WebLoader = field(default=Factory(lambda: WebLoader()), kw_only=True)
    text_chunker: TextChunker = field(default=Factory(lambda: TextChunker(max_tokens=400)), kw_only=True)

    @activity(
        config={
            "description": "Can be used to browse a web page and load its content",
            "schema": Schema({Literal("url", description="Valid HTTP URL"): str}),
        },
    )
    def get_content(self, params: dict) -> ListArtifact | ErrorArtifact:
        url = params["values"]["url"]

        try:
            result = self.web_loader.load(url)
            chunks = self.text_chunker.chunk(result)

            return ListArtifact(chunks)
        except Exception as e:
            return ErrorArtifact("Error getting page content: " + str(e))
