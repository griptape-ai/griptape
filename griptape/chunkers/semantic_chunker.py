from __future__ import annotations

import re
from typing import Optional, Literal, cast

import numpy as np
from attr import Factory, define, field
from numpy.linalg import norm

from griptape.artifacts import TextArtifact
from griptape.chunkers import BaseChunker
from griptape.drivers.embedding.base_embedding_driver import BaseEmbeddingDriver


@define
class SemanticChunker(BaseChunker):
    @define
    class Sentence:
        sentence: TextArtifact = field()
        index: int = field()
        combined_sentence: Optional[TextArtifact] = field(default=None)
        distance_to_next: Optional[float] = field(default=None)

    BreakpointThresholdType = Literal["percentile", "standard_deviation", "interquartile"]

    BREAKPOINT_DEFAULTS: dict[BreakpointThresholdType, float] = {
        "percentile": 95,
        "standard_deviation": 3,
        "interquartile": 1.5,
    }

    embedding_driver: BaseEmbeddingDriver = field(kw_only=True)
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.max_input_tokens, takes_self=True), kw_only=True
    )
    breakpoint_threshold_type: BreakpointThresholdType = field(default="percentile", kw_only=True)
    breakpoint_threshold_amount: int = field(
        default=Factory(lambda self: self.BREAKPOINT_DEFAULTS[self.breakpoint_threshold_type], takes_self=True),
        kw_only=True,
    )

    def try_chunk(self, text: TextArtifact | str) -> list[TextArtifact]:
        sentences = self._text_to_sentences(text.value if isinstance(text, TextArtifact) else text)
        print(f"Num sentences: {len(sentences)}")
        combined_sentences = self._combine_sentences(sentences)
        print(f"Num combined sentences: {len(combined_sentences)}")
        embedded_sentences = self._embed_sentences(combined_sentences)
        print(f"Num embedded sentences: {len(embedded_sentences)}")
        distances, sentences_with_distances = self._calculate_cosine_distances(embedded_sentences)
        chunks = self._combine_sentences_to_chunks(distances, sentences_with_distances)

        return chunks

    def _text_to_sentences(self, text: str) -> list[SemanticChunker.Sentence]:
        sentences = re.split(r"(?<=[.?!])\s+", text)  # TODO: replace with a better sentence tokenizer

        return [
            SemanticChunker.Sentence(sentence=TextArtifact(sentence), index=index)
            for index, sentence in enumerate(sentences)
        ]

    def _combine_sentences(
        self, sentences: list[SemanticChunker.Sentence], buffer_size=1
    ) -> list[SemanticChunker.Sentence]:
        # Go through each sentence dict
        for i in range(len(sentences)):
            # Create a string that will hold the sentences which are joined
            combined_sentence = ""

            # Add sentences before the current one, based on the buffer size.
            for j in range(i - buffer_size, i):
                # Check if the index j is not negative (to avoid index out of range like on the first one)
                if j >= 0:
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += sentences[j].sentence.value + " "

            # Add the current sentence
            combined_sentence += sentences[i].sentence.value

            # Add sentences after the current one, based on the buffer size
            for j in range(i + 1, i + 1 + buffer_size):
                # Check if the index j is within the range of the sentences list
                if j < len(sentences):
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += " " + sentences[j].sentence.value

            # Then add the whole thing to your dict
            # Store the combined sentence in the current sentence dict
            sentences[i].combined_sentence = TextArtifact(combined_sentence)

        return sentences

    def _embed_sentences(self, sentences: list[SemanticChunker.Sentence]) -> list[SemanticChunker.Sentence]:
        for sentence in sentences:
            sentence.combined_sentence.generate_embedding(self.embedding_driver)
            print(f"Sentence {sentence.index} embedded")

        return sentences

    def _calculate_cosine_distances(
        self, sentences: list[SemanticChunker.Sentence]
    ) -> tuple[list[float], list[SemanticChunker.Sentence]]:
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = np.array(sentences[i].combined_sentence.embedding)
            embedding_next = np.array(sentences[i + 1].combined_sentence.embedding)

            # Calculate cosine similarity
            similarity = np.dot(embedding_current, embedding_next) / (norm(embedding_current) * norm(embedding_next))

            # Convert to cosine distance
            distance = 1 - similarity

            distances.append(distance)

            sentences[i].distance_to_next = distance

        return distances, sentences

    def _combine_sentences_to_chunks(
        self, distances: list[float], sentences: list[SemanticChunker.Sentence]
    ) -> list[TextArtifact]:
        breakpoint_distance_threshold = self._calculate_breakpoint_threshold(distances)
        indices_above_thresh = [
            i for i, x in enumerate(distances) if x > breakpoint_distance_threshold
        ]  # The indices of those breakpoints on your list

        # Initialize the start index
        start_index = 0

        # Create a list to hold the grouped sentences
        chunks: list[TextArtifact] = []

        # Iterate through the breakpoints to slice the sentences
        for index in indices_above_thresh:
            # The end index is the current breakpoint
            end_index = index

            # Slice the sentence_dicts from the current start index to the end index
            group = sentences[start_index : end_index + 1]
            combined_text = " ".join([d.sentence.value for d in group])
            chunks.append(TextArtifact(combined_text))

            # Update the start index for the next group
            start_index = index + 1

        # The last group, if any sentences remain
        if start_index < len(sentences):
            combined_text = " ".join([d.sentence.value for d in sentences[start_index:]])
            chunks.append(TextArtifact(combined_text))

        return chunks

    def _calculate_breakpoint_threshold(self, distances: list[float]) -> float:
        if self.breakpoint_threshold_type == "percentile":
            return cast(float, np.percentile(distances, self.breakpoint_threshold_amount))
        elif self.breakpoint_threshold_type == "standard_deviation":
            return cast(float, np.mean(distances) + self.breakpoint_threshold_amount * np.std(distances))
        elif self.breakpoint_threshold_type == "interquartile":
            q1, q3 = np.percentile(distances, [25, 75])
            iqr = q3 - q1

            return np.mean(distances) + self.breakpoint_threshold_amount * iqr
        else:
            raise ValueError(f"Got unexpected `breakpoint_threshold_type`: " f"{self.breakpoint_threshold_type}")
