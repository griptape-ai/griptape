from __future__ import annotations

from urllib.parse import urljoin

import requests
from attrs import Factory, define, field

from griptape.tokenizers import BaseTokenizer


@define()
class GrokTokenizer(BaseTokenizer):
    # https://docs.x.ai/docs/models?cluster=us-east-1#model-constraints
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {
        "grok-2-vision": 32768,
        "grok-2": 131072,
        "grok-vision-beta": 8192,
        "grok-beta": 131072,
    }

    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"grok": 4096}

    base_url: str = field(default="https://api.x.ai", kw_only=True, metadata={"serializable": True})
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )

    def count_tokens(self, text: str) -> int:
        response = requests.post(
            urljoin(self.base_url, "/v1/tokenize-text"),
            headers=self.headers,
            json={"text": text, "model": self.model},
        )
        response.raise_for_status()
        return len(response.json()["token_ids"])
