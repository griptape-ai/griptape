from __future__ import annotations

from attr import Factory, define, field

from griptape.artifacts import BlobArtifact, TextArtifact
from griptape.defaults import BaseDefaultsProvider
from griptape.drivers import BaseEmbeddingDriver, BasePromptDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.memory import TaskMemory
from griptape.tokenizers import OpenAiTokenizer


@define
class StructureDefaultsProvider(BaseDefaultsProvider):
    prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
    embedding_driver: BaseEmbeddingDriver = field(default=OpenAiEmbeddingDriver(), kw_only=True)
    task_memory: TaskMemory = field(
        default=Factory(
            lambda self: TaskMemory(
                artifact_storages={
                    TextArtifact: self.task_memory_defaults_provider.text_artifact_storage,
                    BlobArtifact: self.task_memory_defaults_provider.blob_artifact_storage,
                }
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
