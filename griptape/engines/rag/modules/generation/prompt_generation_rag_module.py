from typing import Callable
from attrs import define, field, Factory
from griptape.artifacts.text_artifact import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseGenerationRagModule
from griptape.utils import J2


@define(kw_only=True)
class PromptGenerationRagModule(BaseGenerationRagModule):
    answer_token_offset: int = field(default=400)
    prompt_driver: BasePromptDriver = field()
    generate_system_template: Callable[[list[str], list[str], list[str]], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True)
    )

    def run(self, context: RagContext) -> RagContext:
        query = context.query
        before_query = context.before_query
        after_query = context.after_query
        text_artifact_chunks = context.text_chunks

        if query:
            tokenizer = self.prompt_driver.tokenizer
            text_chunks = []
            system_prompt = self.generate_system_template(text_chunks, before_query, after_query)

            for artifact in text_artifact_chunks:
                text_chunks.append(artifact.value)

                system_prompt = self.generate_system_template(text_chunks, before_query, after_query)
                message_token_count = self.prompt_driver.tokenizer.count_tokens(
                    self.prompt_driver.prompt_stack_to_string(self.generate_query_prompt_stack(system_prompt, query))
                )

                if message_token_count + self.answer_token_offset >= tokenizer.max_input_tokens:
                    text_chunks.pop()

                    system_prompt = self.generate_system_template(text_chunks, before_query, after_query)

                    break

            output = self.prompt_driver.run(self.generate_query_prompt_stack(system_prompt, query)).to_artifact()

            if isinstance(output, TextArtifact):
                context.output = output
            else:
                raise ValueError("Prompt driver did not return a TextArtifact")

        return context

    def default_system_template_generator(
        self, text_chunks: list[str], before_system_prompt: list, after_system_prompt: list
    ) -> str:
        return J2("engines/rag/modules/prompt_generation/system.j2").render(
            text_chunks=text_chunks,
            before_system_prompt="\n\n".join(before_system_prompt),
            after_system_prompt="\n\n".join(after_system_prompt),
        )
