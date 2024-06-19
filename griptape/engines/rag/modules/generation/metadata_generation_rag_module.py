from typing import Optional
from attrs import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseBeforeGenerationRagModule
from griptape.utils import J2


@define(kw_only=True)
class MetadataGenerationRagModule(BaseBeforeGenerationRagModule):
    metadata: Optional[str] = field(default=None)

    def run(self, context: RagContext) -> RagContext:
        metadata = self.metadata or context.metadata

        if metadata:
            context.before_query.append(
                J2("engines/rag/modules/metadata_generation/system.j2").render(metadata=metadata)
            )

        return context
