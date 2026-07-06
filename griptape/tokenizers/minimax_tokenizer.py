from __future__ import annotations

from attrs import define

from griptape.tokenizers import OpenAiTokenizer


@define()
class MinimaxTokenizer(OpenAiTokenizer):
    # MiniMax exposes an OpenAI-compatible API without a dedicated tokenization
    # endpoint, so token counting reuses the OpenAI tiktoken logic.
    # https://www.minimax.io/platform/document/text_api
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"MiniMax": 1000000}
