from attr import define
from griptape.drivers import BaseEmbeddingModelDriver


@define
class SageMakerHuggingFaceEmbeddingModelDriver(BaseEmbeddingModelDriver):
    def chunk_to_model_params(self, chunk: str) -> dict:
        return {"text_inputs": chunk}

    def process_output(self, output: dict) -> list[float]:
        return output["embedding"][0]
