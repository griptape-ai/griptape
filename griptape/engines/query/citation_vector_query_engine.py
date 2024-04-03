from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact, DerivedArtifactMeta
from griptape.utils import PromptStack
from griptape.engines import BaseQueryEngine
from griptape.utils.j2 import J2
from griptape.rules import Ruleset
from schema import Schema, And, Use


if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver


@define
class CitationVectorQueryEngine(BaseQueryEngine):
    answer_token_offset: int = field(default=400, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(kw_only=True)
    user_template_generator: J2 = field(default=Factory(lambda: J2("engines/query/user.j2")), kw_only=True)
    system_template_generator: J2 = field(default=Factory(lambda: J2("engines/query/citation_system.j2")), kw_only=True)

    def query(
        self,
        query: str,
        namespace: Optional[str] = None,
        *,
        rulesets: Optional[list[Ruleset]] = None,
        metadata: Optional[str] = None,
        top_n: Optional[int] = None,
        filter: Optional[dict] = None,
    ) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        result = self.vector_store_driver.query(query, top_n, namespace, filter=filter)
        text_artifacts = ListArtifact(
            [
                artifact
                for artifact in [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta]
                if isinstance(artifact, TextArtifact)
            ]
        )
        source_artifacts = self._flatten_derived_artifacts(text_artifacts)
        sources = []
        user_message = ""
        system_message = ""

        for source_artifact in source_artifacts:
            sources.append(source_artifact)
            system_message = self.system_template_generator.render(
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets), metadata=metadata, sources=sources
            )
            user_message = self.user_template_generator.render(query=query)

            message_token_count = self.prompt_driver.token_count(
                PromptStack(
                    inputs=[
                        PromptStack.Input(system_message, role=PromptStack.SYSTEM_ROLE),
                        PromptStack.Input(user_message, role=PromptStack.USER_ROLE),
                    ]
                )
            )

            if message_token_count + self.answer_token_offset >= tokenizer.max_input_tokens:
                sources.pop()

                user_message = self.user_template_generator.render(query=query)

                break

        text_artifact = self.prompt_driver.run(
            PromptStack(
                inputs=[
                    PromptStack.Input(system_message, role=PromptStack.SYSTEM_ROLE),
                    PromptStack.Input(user_message, role=PromptStack.USER_ROLE),
                ]
            )
        )
        value_and_sources = Schema(
            And(Use(json.loads), {"value": str, "sources": [And(int, lambda n: 1 <= n <= len(sources))]})
        ).validate(text_artifact.value)
        value = value_and_sources["value"]
        source_indices = value_and_sources["sources"]
        sources = ListArtifact([sources[i - 1] for i in source_indices])
        return TextArtifact(value=value, meta=DerivedArtifactMeta(sources=sources))

    def _flatten_derived_artifacts(self, sources: ListArtifact) -> ListArtifact:
        source_artifacts = []
        for source in sources:
            if isinstance(source.meta, DerivedArtifactMeta):
                # We want to sort the original sources as much as possible. If this is a derived artifact,
                # then we should recursively get the source artifacts which it was derived from. This is
                # important when for example, a derived artifact cites multiple other artifacts, since the
                # the newest artifact we are returning as a result of `query` may only reference one of them.
                source_artifacts.extend(self._flatten_derived_artifacts(source.meta.sources).value)
            else:
                # The original source may or may not have the `SourceMeta` metadata. If it doesn't, then the
                # resulting TextArtifact will cite the original text artifact, it just won't have any kind of
                # reference to where it came from (e.g. url, etc).
                source_artifacts.append(source)
        return ListArtifact(source_artifacts)

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        result = self.vector_store_driver.upsert_text_artifact(artifact, namespace=namespace)

        return result

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: str) -> None:
        self.vector_store_driver.upsert_text_artifacts({namespace: artifacts})

    def load_artifacts(self, namespace: str) -> ListArtifact:
        result = self.vector_store_driver.load_entries(namespace)
        artifacts = [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta and r.meta.get("artifact")]

        return ListArtifact([a for a in artifacts if isinstance(a, TextArtifact)])
