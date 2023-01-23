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
    TEMPLATES_PATH = "prompts/templates"

    @classmethod
    def j2(cls, path: str = TEMPLATES_PATH) -> Environment:
        import galaxybrain

        templates_dir = os.path.join(galaxybrain.PACKAGE_ABS_PATH, path)

        return Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    @classmethod
    def summarize(cls, summary: str, steps: list[Step], path: str = TEMPLATES_PATH, template: str = "summarize.j2") -> str:
        return cls.j2(path).get_template(template).render(summary=summary, steps=steps)

    @classmethod
    def intro(cls, rules: list[Rule], path: str = TEMPLATES_PATH, template: str = "rules.j2") -> str:
        return cls.j2(path).get_template(template).render(rules=rules)

    @classmethod
    def conversation(cls, workflow: Workflow, path: str = TEMPLATES_PATH, template: str = "conversation.j2") -> str:
        return cls.j2(path).get_template(template).render(
            summary=workflow.memory.summary,
            steps=workflow.memory.unsummarized_steps()
        )
