from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Callable

from attrs import Factory, define, field

from griptape import utils
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.engines.rag.modules import BaseRetrievalRagModule

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.drivers import BaseVectorStoreDriver
    from griptape.engines.rag import RagContext
    from griptape.loaders import BaseTextLoader


@define(kw_only=True)
class TextLoaderRetrievalRagModule(BaseRetrievalRagModule):
    loader: BaseTextLoader = field()
    vector_store_driver: BaseVectorStoreDriver = field()
    source: Any = field()
    query_params: dict[str, Any] = field(factory=dict)
    process_query_output_fn: Callable[[list[BaseVectorStoreDriver.Entry]], Sequence[TextArtifact]] = field(
        default=Factory(lambda: lambda es: [e.to_artifact() for e in es]),
    )

    def run(self, context: RagContext) -> Sequence[TextArtifact]:
        namespace = uuid.uuid4().hex
        context_source = self.get_context_param(context, "source")
        source = self.source if context_source is None else context_source

        query_params = utils.dict_merge(self.query_params, self.get_context_param(context, "query_params"))

        query_params["namespace"] = namespace

        loader_output = self.loader.load(source)

        if isinstance(loader_output, ErrorArtifact):
            raise Exception(loader_output.to_text() if loader_output.exception is None else loader_output.exception)
        else:
            self.vector_store_driver.upsert_text_artifacts({namespace: loader_output})

            return self.process_query_output_fn(self.vector_store_driver.query(context.query, **query_params))
