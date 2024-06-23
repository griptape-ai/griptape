from typing import Callable
from attrs import define, field, Factory
from griptape import utils
from griptape.drivers import BasePromptDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseQueryRagModule
from griptape.utils import J2


@define(kw_only=True)
class RelatedQueryGenerationRagModule(BaseQueryRagModule):
    query_count: int = field(default=5)
    prompt_driver: BasePromptDriver = field()
    generate_system_template: Callable[[str], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True), kw_only=True
    )

    def run(self, context: RagContext) -> list[str]:
        system_prompt = self.generate_system_template(context.initial_query)

        results = utils.execute_futures_list(
            [
                self.futures_executor.submit(
                    self.prompt_driver.run, self.generate_query_prompt_stack(system_prompt, "Alternative query: ")
                )
                for _ in range(self.query_count)
            ]
        )

        return [r.value for r in results]

    def default_system_template_generator(self, initial_query: str) -> str:
        return J2("engines/rag/modules/query_generation/system.j2").render(initial_query=initial_query)
