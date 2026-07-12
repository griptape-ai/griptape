from __future__ import annotations

from attrs import define

from griptape.tokenizers import OpenAiTokenizer


@define()
class MinimaxTokenizer(OpenAiTokenizer):
    # MiniMax does not expose a public token-counting endpoint, so token counting
    # uses local tiktoken logic.
    # https://platform.minimax.io/docs/api-reference/api-overview
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {
        "MiniMax-M3": 1_000_000,
        "MiniMax-M2.7": 204_800,
    }
