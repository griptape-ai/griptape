from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional
from abc import ABC, abstractmethod
from llama_index import GPTVectorStoreIndex, Document
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.summarizers import PromptDriverSummarizer
from attr import define, field
from griptape.drivers import OpenAiPromptDriver

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class BaseTextStorageDriver(ABC):
    prompt_driver: BasePromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)

    def query_record(self, key: str, query: str) -> Union[TextArtifact, ErrorArtifact]:
        text = self.load(key)

        if text:
            index = GPTVectorStoreIndex.from_documents([Document(text)])
            query_engine = index.as_query_engine()

            return TextArtifact(
                str(query_engine.query(query)).strip()
            )
        else:
            return ErrorArtifact("Entry not found")

    def summarize_record(self, key: str) -> Union[TextArtifact, ErrorArtifact]:
        text = self.load(key)

        if text:
            summary = PromptDriverSummarizer(
                driver=self.prompt_driver
            ).summarize_text(text)

            return TextArtifact(summary)
        else:
            return ErrorArtifact("Entry not found")

    @abstractmethod
    def save(self, value: any) -> str:
        ...

    @abstractmethod
    def load(self, key: str) -> Optional[any]:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
