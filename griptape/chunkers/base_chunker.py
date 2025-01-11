from __future__ import annotations

from abc import ABC
from typing import Optional

from attrs import Attribute, Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.chunkers import ChunkSeparator
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


@define
class BaseChunker(ABC):
    DEFAULT_SEPARATORS = [ChunkSeparator(" ")]

    separators: list[ChunkSeparator] = field(
        default=Factory(lambda self: self.DEFAULT_SEPARATORS, takes_self=True),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.max_input_tokens, takes_self=True),
        kw_only=True,
    )

    @max_tokens.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_max_tokens(self, _: Attribute, max_tokens: int) -> None:
        if max_tokens < 0:
            raise ValueError("max_tokens must be 0 or greater.")

    def chunk(self, text: TextArtifact | ListArtifact | str) -> list[TextArtifact]:
        text = text.to_text() if isinstance(text, (TextArtifact, ListArtifact)) else text

        return [TextArtifact(c) for c in self._chunk_recursively(text)]

    def _chunk_recursively(self, chunk: str, current_separator: Optional[ChunkSeparator] = None) -> list[str]:
        token_count = self.tokenizer.count_tokens(chunk)
        half_token_count = token_count // 2

        if token_count <= self.max_tokens:
            return [chunk]
        else:
            # If a separator is provided, only use separators after it.
            separators = (
                self.separators[self.separators.index(current_separator) :] if current_separator else self.separators
            )

            # Loop through available separators to find the best split.
            for separator in separators:
                # Split the chunk into subchunks using the current separator.
                subchunks = list(filter(None, chunk.split(separator.value)))

                # We can only recurse if there are multiple subchunks.
                if len(subchunks) > 1:
                    # Find what combination of subchunks results in the most balanced split of the chunk.
                    midpoint_index = self.__find_midpoint_index(subchunks, half_token_count)

                    # Create the two subchunks based on the best separator.
                    first_subchunk, second_subchunk = self.__get_subchunks(separator, subchunks, midpoint_index)

                    # Continue recursively chunking the subchunks.
                    first_subchunk_rec = self._chunk_recursively(first_subchunk.strip(), separator)
                    second_subchunk_rec = self._chunk_recursively(second_subchunk.strip(), separator)

                    # Return the concatenated results of the subchunks if both are non-empty.
                    if first_subchunk_rec and second_subchunk_rec:
                        return first_subchunk_rec + second_subchunk_rec
                    # If only one subchunk is non-empty, return it.
                    elif first_subchunk_rec:
                        return first_subchunk_rec
                    elif second_subchunk_rec:
                        return second_subchunk_rec
                    else:
                        return []
            # If none of the separators result in a balanced split, split the chunk in half.
            midpoint = len(chunk) // 2
            return self._chunk_recursively(chunk[:midpoint]) + self._chunk_recursively(chunk[midpoint:])

    def __get_subchunks(self, separator: ChunkSeparator, subchunks: list[str], balance_index: int) -> tuple[str, str]:
        # Create the two subchunks based on the best separator.
        if separator.is_prefix:
            # If the separator is a prefix, append it before this subchunk.
            first_subchunk = separator.value + separator.value.join(subchunks[: balance_index + 1])
            second_subchunk = separator.value + separator.value.join(subchunks[balance_index + 1 :])
        else:
            # If the separator is not a prefix, append it after this subchunk.
            first_subchunk = separator.value.join(subchunks[: balance_index + 1]) + separator.value
            second_subchunk = separator.value.join(subchunks[balance_index + 1 :])

        return first_subchunk, second_subchunk

    def __find_midpoint_index(self, subchunks: list[str], half_token_count: int) -> int:
        midpoint_index = -1
        best_midpoint_distance = float("inf")

        for index, _ in enumerate(subchunks):
            subchunk_tokens_count = self.tokenizer.count_tokens("".join(subchunks[: index + 1]))

            midpoint_distance = abs(subchunk_tokens_count - half_token_count)
            if midpoint_distance < best_midpoint_distance:
                midpoint_index = index
                best_midpoint_distance = midpoint_distance

        return midpoint_index
