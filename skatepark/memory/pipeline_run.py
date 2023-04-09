import uuid

from attr import define, field, Factory

from skatepark.utils import J2


@define
class PipelineRun:
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    input: str = field(kw_only=True)
    output: str = field(kw_only=True)

    def render(self) -> str:
        return J2("prompts/run_context.j2").render(
            run=self
        )
