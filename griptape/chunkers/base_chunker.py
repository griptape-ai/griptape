from abc import ABC
from typing import Optional, Union
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.tokenizers import TiktokenTokenizer


@define
class BaseChunker(ABC):
    separators: list[str] = field(
        default=Factory(lambda self: self.DEFAULT_SEPARATORS, takes_self=True),
        kw_only=True
    )
    tokenizer: TiktokenTokenizer = field(
        default=TiktokenTokenizer(),
        kw_only=True
    )
    max_tokens_per_chunk: int = field(
        default=Factory(lambda self: self.tokenizer.max_tokens, takes_self=True),
        kw_only=True
    )

    def chunk(self, chunk: Union[TextArtifact, str]) -> list[TextArtifact]:
        return self._chunk_recursively(chunk)

    def _chunk_recursively(
            self, chunk: Union[TextArtifact, str], current_separator: Optional[str] = None
    ) -> list[TextArtifact]:
        chunk = chunk.value if isinstance(chunk, TextArtifact) else chunk
        token_count = self.tokenizer.token_count(chunk)

        if token_count <= self.max_tokens_per_chunk:
            return [TextArtifact(chunk)]
        else:
            balance_index = -1
            balance_diff = float("inf")
            tokens_count = 0
            half_token_count = token_count // 2

            if current_separator:
                separators = self.separators[self.separators.index(current_separator):]
            else:
                separators = self.separators

            for separator in separators:
                subchanks = list(filter(None, chunk.split(separator)))

                if len(subchanks) > 1:
                    for index, subchunk in enumerate(subchanks):
                        if index < len(subchanks):
                            subchunk = subchunk + separator

                        tokens_count += self.tokenizer.token_count(subchunk)

                        if abs(tokens_count - half_token_count) < balance_diff:
                            balance_index = index
                            balance_diff = abs(tokens_count - half_token_count)

                    first_subchunk = self._chunk_recursively(
                        (separator.join(subchanks[:balance_index + 1]) + separator).strip(),
                        separator
                    )
                    second_subchunk = self._chunk_recursively(
                        separator.join(subchanks[balance_index + 1:]).strip(),
                        separator
                    )

                    if first_subchunk and second_subchunk:
                        return first_subchunk + second_subchunk
                    elif first_subchunk:
                        return first_subchunk
                    elif second_subchunk:
                        return second_subchunk
                    else:
                        return []
            return []
