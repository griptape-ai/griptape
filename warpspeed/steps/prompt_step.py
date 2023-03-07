from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from warpspeed.utils import J2
from warpspeed.steps import Step
from warpspeed.artifacts import TextOutput

if TYPE_CHECKING:
    from warpspeed.drivers import PromptDriver


@define
class PromptStep(Step):
    prompt_template: str = field()
    context: dict[str, any] = field(factory=dict, kw_only=True)
    driver: Optional[PromptDriver] = field(default=None, kw_only=True)

    def run(self) -> TextOutput:
        self.output = self.active_driver().run(value=self.structure.to_prompt_string(self))

        return self.output

    def active_driver(self) -> PromptDriver:
        if self.driver is None:
            return self.structure.prompt_driver
        else:
            return self.driver

    def render_prompt(self) -> str:
        return J2().render_from_string(
            self.prompt_template,
            **self.full_context
        )

    def render(self) -> str:
        return J2("prompts/steps/prompt.j2").render(
            step=self
        )

    @property
    def full_context(self) -> dict[str, any]:
        prompt_context = self.default_context

        prompt_context.update(self.context)

        return prompt_context

    @property
    def default_context(self) -> dict[str, any]:
        return {
            "inputs": {parent.id: parent.output.value if parent.output else "" for parent in self.parents},
            "structure": self.structure,
            "parents": {parent.id: parent for parent in self.parents},
            "children": {child.id: child for child in self.children}
        }
