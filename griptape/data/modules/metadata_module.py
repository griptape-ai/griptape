from attr import define, field
from griptape.data.modules import BaseModule
from griptape.utils import J2


@define
class MetadataModule(BaseModule):
    metadata: str = field(kw_only=True)

    def process(self, context: dict) -> dict:
        metadata_text = J2("data/modules/metadata/system.j2").render(metadata=self.metadata)

        if not context.get("before_text_query"):
            context["before_text_query"] = []

        context["before_text_query"].append(metadata_text)

        return context
