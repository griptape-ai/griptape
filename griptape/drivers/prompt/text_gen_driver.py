import copy
import requests
from attr import define, field
from typing import Optional
from urllib.parse import urljoin
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TextGenTokenizer


@define
class TextGenPromptDriver(BasePromptDriver):
    """
    Prompt Driver for the text-generation-webui https://github.com/oobabooga/text-generation-webui

    params usage example:
    https://github.com/oobabooga/text-generation-webui/blob/main/api-examples/api-example.py
    """
    preset: Optional[str] = field(default=None, kw_only=True)
    params: dict = field(factory=dict, kw_only=True)

    model_url: str = field(default="http://localhost:5000", kw_only=True)
    generate_uri: str = field(default="/api/v1/generate", kw_only=True)

    model: Optional[str] = field(default=None, kw_only=True)
    tokenizer: TextGenTokenizer = field(kw_only=True)

    def try_run(self, value: str) -> TextArtifact:

        url = urljoin(self.model_url, self.generate_uri)

        if self.preset is None:
            request = copy.deepcopy(self.params)
        else:
            request = {"preset": self.preset}

        request["prompt"] = value
        response = requests.post(url, json=request)

        if response.status_code == 200:
            result = response.json()["results"][0]["text"]
        else:
            raise Exception(f"Failed to obtain valid response. error response: {response} ")

        return TextArtifact(value=result)
