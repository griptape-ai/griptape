from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from attr import define, field, Factory
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import BaseQueryEngine
from griptape.tokenizers import OpenAiTokenizer
from griptape.utils import J2, PromptStack

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact, ListArtifact
    from griptape.drivers import BaseGraphDriver, BasePromptDriver
    from griptape.rules import Ruleset


@define
class GraphQueryEngine(BaseQueryEngine):
    graph_driver: BaseGraphDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)),
        kw_only=True,
    )
    template_generator: J2 = field(default=Factory(lambda: J2("engines/query/graph_query.j2")), kw_only=True)

    def load_metadata(self, namespace: Optional[str] = None) -> dict:
        return self.graph_driver.load_metadata(namespace)

    def query(
            self,
            query: str,
            namespace: Optional[str] = None,
            metadata: Optional[str] = None,
            rulesets: Optional[list[Ruleset]] = None
    ) -> TextArtifact:
        message = self.template_generator.render(
            metadata=metadata,
            question=query,
            graph_structure=self.graph_driver.load_metadata(namespace),
            graph_db_hint=self.graph_driver.graph_db_hint,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )
        cypher_query = self.prompt_driver.run(
            PromptStack(inputs=[PromptStack.Input(message, role=PromptStack.USER_ROLE)])
        ).value

        print(cypher_query)

        return self.graph_driver.query(cypher_query, namespace)

    def load_artifacts(self, namespace: Optional[str] = None) -> ListArtifact:
        return self.graph_driver.load_artifacts(namespace)

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        return self.graph_driver.upsert_text_artifact(artifact, namespace)

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> list[str]:
        return self.graph_driver.upsert_text_artifacts(artifacts, namespace)
