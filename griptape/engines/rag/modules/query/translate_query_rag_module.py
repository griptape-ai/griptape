from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import Factory, define, field

from griptape.engines.rag.modules import BaseQueryRagModule
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.engines.rag import RagContext


@define(kw_only=True)
class TranslateQueryRagModule(BaseQueryRagModule):
    prompt_driver: BasePromptDriver = field()
    language: str = field()
    generate_user_template: Callable[[str, str], str] = field(
        default=Factory(lambda self: self.default_generate_user_template, takes_self=True),
    )

    def run(self, context: RagContext) -> RagContext:
        user_prompt = self.generate_user_template(context.query, self.language)
        output = self.prompt_driver.run(self.generate_prompt_stack(None, user_prompt)).to_artifact()

        context.query = output.to_text()

        return context

    def default_generate_user_template(self, query: str, language: str) -> str:
        return J2("engines/rag/modules/query/translate/user.j2").render(query=query, language=language)
