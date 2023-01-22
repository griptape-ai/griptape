from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define
from jinja2 import Environment, FileSystemLoader
import os
from galaxybrain.workflows import StepInput

if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Workflow
    from galaxybrain.rules.rule import Rule


@define
class Prompt(StepInput):
    @classmethod
    def j2(cls):
        import galaxybrain

        templates_path = os.path.join(galaxybrain.PACKAGE_ABS_PATH, "prompts/templates")

        return Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
            lstrip_blocks=True
        )

    @classmethod
    def summarize(cls, summary: str, steps: list[Step]):
        return cls.j2().get_template("summarize.j2").render(summary=summary, steps=steps)

    @classmethod
    def intro(cls, rules: list[Rule]):
        return cls.j2().get_template("rules.j2").render(rules=rules)

    @classmethod
    def conversation(cls, workflow: Workflow):
        return cls.j2().get_template("conversation.j2").render(
            summary=workflow.memory.summary,
            steps=workflow.memory.unsummarized_steps()
        )
