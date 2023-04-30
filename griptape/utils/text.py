from decouple import config
from langchain import OpenAI
from llama_index import GPTSimpleVectorIndex, LLMPredictor


def to_vector_index(text: str) -> GPTSimpleVectorIndex:
    from llama_index import GPTSimpleVectorIndex, Document

    return GPTSimpleVectorIndex(
        [Document(text)],
        llm_predictor=LLMPredictor(
            llm=OpenAI(
                openai_api_key=config("OPENAI_API_KEY")
            )
        )
    )
