from __future__ import annotations
from abc import ABC
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.chunkers import ChunkSeparator
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


@define
class BaseChunker(ABC):
    DEFAULT_SEPARATORS = [ChunkSeparator(" ")]

    separators: list[ChunkSeparator] = field(
        default=Factory(lambda self: self.DEFAULT_SEPARATORS, takes_self=True), kw_only=True
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)), kw_only=True
    )
    max_tokens: int = field(default=Factory(lambda self: self.tokenizer.max_tokens, takes_self=True), kw_only=True)

    def chunk(self, text: TextArtifact | str) -> list[TextArtifact]:
        text = text.value if isinstance(text, TextArtifact) else text

        return [TextArtifact(c) for c in self._chunk_recursively(text)]

    def _chunk_recursively(self, chunk: str, current_separator: ChunkSeparator | None = None) -> list[str]:
        token_count = self.tokenizer.count_tokens(chunk)

        if token_count <= self.max_tokens:
            return [chunk]
        else:
            balance_index = -1
            balance_diff = float("inf")
            tokens_count = 0
            half_token_count = token_count // 2

            # If a separator is provided, only use separators after it.
            if current_separator:
                separators = self.separators[self.separators.index(current_separator) :]
            else:
                separators = self.separators

            # Loop through available separators to find the best split.
            for separator in separators:
                # Split the chunk into subchunks using the current separator.
                subchunks = list(filter(None, chunk.split(separator.value)))

                # Check if the split resulted in more than one subchunk.
                if len(subchunks) > 1:
                    # Iterate through the subchunks and calculate token counts.
                    for index, subchunk in enumerate(subchunks):
                        if index < len(subchunks):
                            if separator.is_prefix:
                                subchunk = separator.value + subchunk
                            else:
                                subchunk = subchunk + separator.value

                        tokens_count += self.tokenizer.count_tokens(subchunk)

                        # Update the best split if the current one is more balanced.
                        if abs(tokens_count - half_token_count) < balance_diff:
                            balance_index = index
                            balance_diff = abs(tokens_count - half_token_count)

                    # Create the two subchunks based on the best separator.
                    if separator.is_prefix:
                        # If the separator is a prefix, append it before this subchunk.
                        first_subchunk = separator.value + separator.value.join(subchunks[: balance_index + 1])
                        second_subchunk = separator.value + separator.value.join(subchunks[balance_index + 1 :])
                    else:
                        # If the separator is not a prefix, append it after this subchunk.
                        first_subchunk = separator.value.join(subchunks[: balance_index + 1]) + separator.value
                        second_subchunk = separator.value.join(subchunks[balance_index + 1 :])

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
