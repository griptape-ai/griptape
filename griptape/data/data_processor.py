from attr import define, field
from griptape.data.modules import BaseModule


@define
class DataProcessor:
    modules: list[BaseModule] = field(factory=list, kw_only=True)

    def process_query(self, query: str) -> dict:
        return self.process(
            {
                "query": query
            }
        )

    def process(self, context: dict) -> dict:
        output = context

        for module in self.modules:
            output = module.process(output)

        return output
