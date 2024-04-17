from typing import Callable
from attr import define, field, Factory
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseGenerationModule
from griptape.tokenizers import OpenAiTokenizer
from griptape.utils import PromptStack, J2


@define(kw_only=True)
class PromptGenerator(BaseGenerationModule):
    answer_token_offset: int = field(default=400, kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    generate_system_template: Callable[[list[str], list[str], list[str]], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True), kw_only=True
    )

    def generate(self, context: RagContext) -> RagContext:
        query = context.query
        before_query = context.before_query
        after_query = context.after_query
        text_artifact_chunks = context.text_chunks

        if query and text_artifact_chunks:
            tokenizer = self.prompt_driver.tokenizer
            text_chunks = []
            system_prompt = ""

            for artifact in text_artifact_chunks:
                text_chunks.append(artifact.value)

                system_prompt = self.generate_system_template(text_chunks, before_query, after_query)
                message_token_count = self.prompt_driver.token_count(
                    self.generate_prompt_stack(system_prompt, query)
                )

                if message_token_count + self.answer_token_offset >= tokenizer.max_input_tokens:
                    text_chunks.pop()

                    system_prompt = self.generate_system_template(text_chunks, before_query, after_query)

                    break

            context.output = self.prompt_driver.run(
                self.generate_prompt_stack(system_prompt, query)
            ).value

        return context

    def generate_prompt_stack(self, system_prompt: str, query: str) -> PromptStack:
        return PromptStack(
            inputs=[
                PromptStack.Input(system_prompt, role=PromptStack.SYSTEM_ROLE),
                PromptStack.Input(query, role=PromptStack.USER_ROLE)
            ]
        )

    def default_system_template_generator(
            self, text_chunks: list[str], before_system_prompt: list, after_system_prompt: list
    ) -> str:
        return J2("engines/rag/modules/prompt_generator/system.j2").render(
            text_chunks=text_chunks,
            before_system_prompt="\n\n".join(before_system_prompt),
            after_system_prompt="\n\n".join(after_system_prompt)
        )
