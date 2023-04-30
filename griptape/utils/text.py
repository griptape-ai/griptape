from llama_index import GPTSimpleVectorIndex, Document


def to_vector_index(text: str) -> GPTSimpleVectorIndex:
    return GPTSimpleVectorIndex(
        [Document(text)]
    )
