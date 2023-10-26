import os
import openai
from griptape.artifacts import BlobArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Optional
import requests


class ImageGenerator(BaseTool):
    api_key = os.environ.get("OPENAI_API_KEY")

    @activity(
        config={
            "description": "Generates single image using DALL·E API based on a provided prompt and returns the image data in bytes if the mode is 'save' or returns the URL of the image if the mode is 'url' ",
            "schema": Schema(
                {
                    "prompt": str,
                    Optional("size", default="1024x1024"): str,
                    Optional("mode", default="url"): str,
                }
            ),
        }
    )
    def dalle_generate(self, params: dict) -> ListArtifact:
        openai.api_key = self.api_key
        prompt_value = params["values"]["prompt"]
        n_value = 1
        size_value = params["values"].get("size", "1024x1024")
        mode_value = params["values"].get("mode", "url")

        response = openai.Image.create(prompt=prompt_value, n=n_value, size=size_value)

        image_url = response["data"][0]["url"]
        if mode_value.lower() == "save":
            response = requests.get(image_url)
            response.raise_for_status()

            return ListArtifact([BlobArtifact(response.content)])
        else:
            return ListArtifact([TextArtifact(image_url)])


# Don't forget to add any necessary API authentication setup for OpenAI.
