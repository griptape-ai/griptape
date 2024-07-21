from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from voyageai import Client


@define()
class VoyageAiTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {
        "voyage-large-2": 16000,
        "voyage-code-2": 16000,
        "voyage-2": 4000,
        "voyage-lite-02-instruct": 4000,
    }
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"voyage": 0}

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    client: Client = field(
        default=Factory(
            lambda self: import_optional_dependency("voyageai").Client(api_key=self.api_key),
            takes_self=True,
        ),
        kw_only=True,
    )

    def count_tokens(self, text: str) -> int:
        return self.client.count_tokens([text])
