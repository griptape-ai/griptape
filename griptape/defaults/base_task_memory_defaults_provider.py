from __future__ import annotations
from abc import ABC
from attr import define, field, Factory

from griptape.artifacts import BlobArtifact, TextArtifact
from griptape.defaults import BaseDefaultsProvider
from griptape.drivers import BaseEmbeddingDriver, BasePromptDriver, LocalVectorStoreDriver
from griptape.engines import CsvExtractionEngine, JsonExtractionEngine, PromptSummaryEngine, VectorQueryEngine
from griptape.memory.task.storage import BlobArtifactStorage, TextArtifactStorage


@define
class BaseTaskMemoryDefaultsProvider(BaseDefaultsProvider, ABC):
    query_engine_prompt_driver: BasePromptDriver = field(kw_only=True)
    query_engine_embedding_driver: BaseEmbeddingDriver = field(kw_only=True)
    summary_engine_prompt_driver: BasePromptDriver = field(kw_only=True)
    csv_extraction_engine_prompt_driver: BasePromptDriver = field(kw_only=True)
    json_extraction_engine_prompt_driver: BasePromptDriver = field(kw_only=True)
    text_artifact_storage: TextArtifactStorage = field(
        default=Factory(
            lambda self: TextArtifactStorage(
                query_engine=VectorQueryEngine(
                    prompt_driver=self.query_engine_prompt_driver,
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=self.query_engine_prompt_embedding_driver
                    ),
                ),
                summary_engine=PromptSummaryEngine(prompt_driver=self.summary_engine_prompt_driver),
                csv_extraction_engine=CsvExtractionEngine(prompt_driver=self.summary_engine_prompt_driver),
                json_extraction_engine=JsonExtractionEngine(prompt_driver=self.json_extraction_engine_prompt_driver),
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    blob_artifact_storage: BlobArtifactStorage = field(default=BlobArtifactStorage(), kw_only=True)
    artifact_storages: dict = field(
        default=Factory(
            lambda self: {TextArtifact: self.text_artifact_storage, BlobArtifact: self.blob_artifact_storage},
            takes_self=True,
        )
    )
