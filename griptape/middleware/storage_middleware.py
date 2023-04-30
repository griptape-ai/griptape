from __future__ import annotations
from typing import TYPE_CHECKING
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.middleware import BaseMiddleware
from attr import define, field

if TYPE_CHECKING:
    from griptape.drivers import BaseStorageDriver
    from llama_index import GPTSimpleVectorIndex


@define
class StorageMiddleware(BaseMiddleware):
    driver: BaseStorageDriver = field(kw_only=True)

    def process_output(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(value, TextArtifact):
            key = self.driver.save(value.value)
            output = J2("middleware/storage.j2").render(
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
        "description": "Can be used to search a storage entry",
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
            index = self._to_vector_index(text)

            return TextArtifact(
                str(index.query(f"Search query: {value['query']}")).strip()
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
            index = self._to_vector_index(text)

            return TextArtifact(
                str(index.query("What is the summary of this document point-by-point?")).strip()
            )
        else:
            return ErrorArtifact("Entry not found")

    def _to_vector_index(self, text: str) -> GPTSimpleVectorIndex:
        from llama_index import GPTSimpleVectorIndex, Document

        return GPTSimpleVectorIndex([
            Document(text)
        ])
