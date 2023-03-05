from attrs import define, field
from galaxybrain.structures import Pipeline


@define(frozen=True)
class Conversation:
    pipeline: Pipeline = field()

    def lines(self, include_substeps=True) -> list[str]:
        from galaxybrain.steps import BaseToolStep

        lines = []

        for step in self.pipeline.steps:
            lines.append(f"Q: {step.render_prompt()}")

            if include_substeps and isinstance(step, BaseToolStep):
                for substep in step.substeps:
                    lines.append(substep.render())

            lines.append(f"A: {step.output.value}")

        return lines

    def to_string(self, include_substeps=True) -> str:
        return str.join("\n", self.lines(include_substeps))
