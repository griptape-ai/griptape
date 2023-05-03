from __future__ import annotations
from typing import TYPE_CHECKING
from llama_index import Document, GPTVectorStoreIndex
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.ramps import BaseRamp
from attr import define, field
from griptape.summarizers import PromptDriverSummarizer
from griptape.drivers import OpenAiPromptDriver

if TYPE_CHECKING:
    from griptape.drivers import BaseStorageDriver, BasePromptDriver


@define
class StorageRamp(BaseRamp):
    driver: BaseStorageDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)

    def process_output(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(value, TextArtifact):
            key = self.driver.save(value.value)
            output = J2("ramps/storage.j2").render(
                storage_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.config["name"],
                key=key
            )

            return TextArtifact(output)
        else:
            return value

    @activity(config={
        "name": "search_entry",
        "description": "Can be used to search a storage entry for any content",
        "schema": Schema({
            Literal(
                "id",
                description="Storage entry ID"
            ): str,
            Literal(
                "query",
                description="Search query to run against the storage entry"
            ): str
        })
    })
    def search_entry(self, value: dict) -> BaseArtifact:
        text = self.driver.load(value["id"])

        if text:
            index = GPTVectorStoreIndex.from_documents([Document(text)])
            query_engine = index.as_query_engine()

            return TextArtifact(
                str(query_engine.query(f"Search text with query: {value['query']}")).strip()
            )
        else:
            return ErrorArtifact("Entry not found")

    @activity(config={
        "name": "summarize",
        "description": "Can be used to generate a summary of a storage entry",
        "schema": Schema(
            str,
            description="Storage entry ID"
        )
    })
    def summarize(self, value: str) -> BaseArtifact:
        text = self.driver.load(value)

        if text:
            summary = PromptDriverSummarizer(
                driver=self.prompt_driver
            ).summarize_text(text)

            return TextArtifact(summary)
        else:
            return ErrorArtifact("Entry not found")
