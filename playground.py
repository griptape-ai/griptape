from pathlib import Path
from griptape.engines import VectorQueryEngine
from griptape.drivers import GeminiEmbeddingDriver, LocalVectorStoreDriver, OpenAiChatPromptDriver
from griptape.loaders import TextLoader

engine = VectorQueryEngine(
    prompt_driver=OpenAiChatPromptDriver(
        api_key="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", temperature=0, model="gpt-4"
    ),
    vector_store_driver=LocalVectorStoreDriver(embedding_driver=GeminiEmbeddingDriver()),
)

engine.upsert_text_artifacts(TextLoader().load(Path("./_Inputs.txt")), namespace="test")

test = engine.query("What is the action about?")

print(test)
