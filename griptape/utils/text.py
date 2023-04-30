from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llama_index import GPTSimpleVectorIndex


def to_vector_index(text: str) -> GPTSimpleVectorIndex:
    from llama_index import GPTSimpleVectorIndex, Document

    return GPTSimpleVectorIndex([
        Document(text)
    ])
