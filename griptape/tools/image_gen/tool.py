from __future__ import annotations
import os
import openai
from griptape.artifacts import (
    BlobArtifact,
    ListArtifact,
    TextArtifact,
    ErrorArtifact,
    InfoArtifact,
)
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Optional
from attr import define, field, Factory
from typing import Optional as TypingOptional
import requests


@define
class DalleImageGenerator(BaseTool):
    api_key: TypingOptional[str] = field(
        default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True
    )

    @activity(
        config={
            "description": "Generates single image using DALL·E API based on a provided prompt and returns the image data in bytes if the mode is 'download' or returns the URL of the image if the mode is 'url' ",
            "schema": Schema(
                {
                    "prompt": str,
                    Optional("size", default="1024x1024"): str,
                    Optional("mode", default="url"): str,
                }
            ),
        }
    )
    def dalle_generate(self, params: dict) -> ListArtifact | ErrorArtifact:
        openai.api_key = self.api_key

        prompt_value = params["values"]["prompt"]
        n_value = 1
        size_value = params["values"].get("size", "1024x1024")
        mode_value = params["values"].get("mode", "url")
        try:
            response = openai.Image.create(
                prompt=prompt_value, n=n_value, size=size_value
            )
        except Exception as err:
            return ErrorArtifact(str(err))

        image_url = response["data"][0]["url"]
        if mode_value.lower() == "download":
            response = requests.get(image_url)
            try:
                response.raise_for_status()
                return ListArtifact([BlobArtifact(response.content)])
            except requests.exceptions.HTTPError as err:
                return ErrorArtifact(str(err))
        else:
            return ListArtifact([TextArtifact(image_url)])
