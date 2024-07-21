from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.engines.rag.modules import BaseResponseRagModule
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.engines.rag import RagContext


@define(kw_only=True)
class PromptResponseRagModule(BaseResponseRagModule):
    answer_token_offset: int = field(default=400)
    prompt_driver: BasePromptDriver = field()
    generate_system_template: Callable[[RagContext, list[TextArtifact]], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True),
    )

    def run(self, context: RagContext) -> RagContext:
        query = context.query
        tokenizer = self.prompt_driver.tokenizer
        included_chunks = []
        system_prompt = self.generate_system_template(context, included_chunks)

        for artifact in context.text_chunks:
            included_chunks.append(artifact)

            system_prompt = self.generate_system_template(context, included_chunks)
            message_token_count = self.prompt_driver.tokenizer.count_tokens(
                self.prompt_driver.prompt_stack_to_string(self.generate_query_prompt_stack(system_prompt, query)),
            )

            if message_token_count + self.answer_token_offset >= tokenizer.max_input_tokens:
                included_chunks.pop()

                system_prompt = self.generate_system_template(context, included_chunks)

                break

        output = self.prompt_driver.run(self.generate_query_prompt_stack(system_prompt, query)).to_artifact()

        if isinstance(output, TextArtifact):
            context.output = output
        else:
            raise ValueError("Prompt driver did not return a TextArtifact")

        return context

    def default_system_template_generator(self, context: RagContext, artifacts: list[TextArtifact]) -> str:
        return J2("engines/rag/modules/response/prompt/system.j2").render(
            text_chunks=[c.to_text() for c in artifacts],
            before_system_prompt="\n\n".join(context.before_query),
            after_system_prompt="\n\n".join(context.after_query),
        )
