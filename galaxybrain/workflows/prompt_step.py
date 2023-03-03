from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import Step
from galaxybrain.artifacts import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import PromptDriver


@define
class PromptStep(Step):
    prompt_template: str = field()
    context: dict[str, any] = field(factory=dict, kw_only=True)
    driver: Optional[PromptDriver] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        self.output = self.active_driver().run(value=self.workflow.to_prompt_string())

        return self.output

    def active_driver(self) -> PromptDriver:
        if self.driver is None:
            return self.workflow.prompt_driver
        else:
            return self.driver

    def render_prompt(self):
        prompt_context = self.default_context

        prompt_context.update(self.context)

        return J2().render_from_string(
            self.prompt_template,
            **prompt_context
        )

    def render(self) -> str:
        return J2("prompts/steps/prompt.j2").render(
            step=self
        )

    @property
    def default_context(self) -> dict[str, any]:
        return {
            "workflow": self.workflow,
            "input": self.input,
            "parent": self.parent,
            "child": self.child,
        }
