from __future__ import annotations

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.loaders import WebLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class WebScraper(BaseTool):
    web_loader: WebLoader = field(default=Factory(lambda: WebLoader()), kw_only=True)

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
            if isinstance(result, ErrorArtifact):
                return result
            else:
                return ListArtifact(result)
        except Exception as e:
            return ErrorArtifact("Error getting page content: " + str(e))
