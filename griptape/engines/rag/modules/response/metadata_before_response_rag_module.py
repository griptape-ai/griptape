from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.engines.rag.modules import BaseBeforeResponseRagModule
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext


@define(kw_only=True)
class MetadataBeforeResponseRagModule(BaseBeforeResponseRagModule):
    metadata: Optional[str] = field(default=None)

    def run(self, context: RagContext) -> RagContext:
        context_metadata = self.get_context_param(context, "metadata")
        metadata = self.metadata if context_metadata is None else context_metadata

        if metadata is not None:
            context.before_query.append(J2("engines/rag/modules/response/metadata/system.j2").render(metadata=metadata))

        return context
