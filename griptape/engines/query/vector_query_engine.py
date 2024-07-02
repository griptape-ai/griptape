from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact
from griptape.common import PromptStack
from griptape.common.prompt_stack.messages.message import Message
from griptape.engines import BaseQueryEngine
from griptape.utils.j2 import J2
from griptape.rules import Ruleset

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver


@define
class VectorQueryEngine(BaseQueryEngine):
    answer_token_offset: int = field(default=400, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(kw_only=True)
    user_template_generator: J2 = field(default=Factory(lambda: J2("engines/query/user.j2")), kw_only=True)
    system_template_generator: J2 = field(default=Factory(lambda: J2("engines/query/system.j2")), kw_only=True)

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
        artifacts = [
            artifact
            for artifact in [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta]
            if isinstance(artifact, TextArtifact)
        ]
        text_segments = []
        user_message = ""
        system_message = ""

        for artifact in artifacts:
            text_segments.append(artifact.value)
            system_message = self.system_template_generator.render(
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
                metadata=metadata,
                text_segments=text_segments,
            )
            user_message = self.user_template_generator.render(query=query)

            message_token_count = self.prompt_driver.tokenizer.count_input_tokens_left(
                self.prompt_driver.prompt_stack_to_string(
                    PromptStack(
                        messages=[
                            Message(system_message, role=Message.SYSTEM_ROLE),
                            Message(user_message, role=Message.USER_ROLE),
                        ]
                    )
                )
            )

            if message_token_count + self.answer_token_offset >= tokenizer.max_input_tokens:
                text_segments.pop()

                system_message = self.system_template_generator.render(
                    rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
                    metadata=metadata,
                    text_segments=text_segments,
                )

                break

        result = self.prompt_driver.run(
            PromptStack(
                messages=[
                    Message(system_message, role=Message.SYSTEM_ROLE),
                    Message(user_message, role=Message.USER_ROLE),
                ]
            )
        )

        if isinstance(result, TextArtifact):
            return result
        else:
            raise ValueError("Prompt Driver did not return a TextArtifact.")

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        result = self.vector_store_driver.upsert_text_artifact(artifact, namespace=namespace)

        return result

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: str) -> None:
        self.vector_store_driver.upsert_text_artifacts({namespace: artifacts})

    def load_artifacts(self, namespace: str) -> ListArtifact:
        result = self.vector_store_driver.load_entries(namespace)
        artifacts = [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta and r.meta.get("artifact")]

        return ListArtifact([a for a in artifacts if isinstance(a, TextArtifact)])
