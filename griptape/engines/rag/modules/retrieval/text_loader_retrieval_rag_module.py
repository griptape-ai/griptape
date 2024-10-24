from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Callable

from attrs import Factory, define, field

from griptape import utils
from griptape.chunkers import TextChunker
from griptape.engines.rag.modules import BaseRetrievalRagModule

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts import TextArtifact
    from griptape.drivers import BaseVectorStoreDriver
    from griptape.engines.rag import RagContext
    from griptape.loaders import TextLoader


@define(kw_only=True)
class TextLoaderRetrievalRagModule(BaseRetrievalRagModule):
    loader: TextLoader = field()
    chunker: TextChunker = field(default=Factory(lambda: TextChunker()))
    vector_store_driver: BaseVectorStoreDriver = field()
    source: Any = field()
    query_params: dict[str, Any] = field(factory=dict)
    process_query_output: Callable[[list[BaseVectorStoreDriver.Entry]], Sequence[TextArtifact]] = field(
        default=Factory(lambda: lambda es: [e.to_artifact() for e in es]),
    )

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        namespace = uuid.uuid4().hex
        context_source = self.get_context_param(context, "source")
        source = self.source if context_source is None else context_source

        query_params = utils.dict_merge(self.query_params, self.get_context_param(context, "query_params"))

        query_params["namespace"] = namespace

        loader_output = self.loader.load(source)
        chunks = self.chunker.chunk(loader_output)

        self.vector_store_driver.upsert_text_artifacts({namespace: chunks})

        return self.process_query_output(self.vector_store_driver.query(context.query, **query_params))
