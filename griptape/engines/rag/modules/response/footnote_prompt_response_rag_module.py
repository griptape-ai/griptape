from attrs import define

from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import PromptResponseRagModule
from griptape.utils import J2


@define(kw_only=True)
class FootnotePromptResponseRagModule(PromptResponseRagModule):
    def default_system_template_generator(self, context: RagContext, artifacts: list[TextArtifact]) -> str:
        return J2("engines/rag/modules/response/footnote_prompt/system.j2").render(
            text_chunk_artifacts=artifacts,
            references=utils.references_from_artifacts(artifacts),
            before_system_prompt="\n\n".join(context.before_query),
            after_system_prompt="\n\n".join(context.after_query),
        )
