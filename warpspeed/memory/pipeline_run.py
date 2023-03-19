import uuid
from attrs import define, field, Factory
from warpspeed.artifacts import StructureArtifact
from warpspeed.utils import J2


@define
class PipelineRun:
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    prompt: str = field(kw_only=True)
    output: StructureArtifact = field(kw_only=True)

    def render(self) -> str:
        return J2("prompts/run_context.j2").render(
            run=self
        )
