from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Optional

import schema
from attrs import Attribute, Factory, define, field, validators

from griptape.common import Message, PromptStack
from griptape.configs import Defaults
from griptape.engines import BaseEvalEngine
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver

STEPS_SCHEMA = schema.Schema(
    {
        "steps": [str],
    }
)

RESULTS_SCHEMA = schema.Schema(
    {
        "score": float,
        "reason": str,
    }
)


@define(kw_only=True)
class EvalEngine(BaseEvalEngine, SerializableMixin):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    name: str = field(
        default=Factory(lambda self: self.id, takes_self=True),
        metadata={"serializable": True},
    )
    criteria: Optional[str] = field(default=None, metadata={"serializable": True})
    evaluation_steps: Optional[list[str]] = field(default=None, metadata={"serializable": True})
    prompt_driver: BasePromptDriver = field(default=Factory(lambda: Defaults.drivers_config.prompt_driver))
    generate_steps_system_template: J2 = field(default=Factory(lambda: J2("engines/eval/steps/system.j2")))
    generate_steps_user_template: J2 = field(default=Factory(lambda: J2("engines/eval/steps/user.j2")))
    generate_results_system_template: J2 = field(default=Factory(lambda: J2("engines/eval/results/system.j2")))
    generate_results_user_template: J2 = field(default=Factory(lambda: J2("engines/eval/results/user.j2")))

    @criteria.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_criteria(self, _: Attribute, value: Optional[str]) -> None:
        if value is None:
            if self.evaluation_steps is None:
                raise ValueError("either criteria or evaluation_steps must be specified")
            return

        if self.evaluation_steps is not None:
            raise ValueError("can't have both criteria and evaluation_steps specified")

        if not value:
            raise ValueError("criteria must not be empty")

    @evaluation_steps.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_evaluation_steps(self, _: Attribute, value: Optional[list[str]]) -> None:
        if value is None:
            if self.criteria is None:
                raise ValueError("either evaluation_steps or criteria must be specified")
            return

        if self.criteria is not None:
            raise ValueError("can't have both evaluation_steps and criteria specified")

        if not value:
            raise ValueError("evaluation_steps must not be empty")

    def evaluate(self, input: str, actual_output: str, **kwargs) -> tuple[float, str]:  # noqa: A002
        evaluation_params = {
            key.replace("_", " ").title(): value
            for key, value in {"input": input, "actual_output": actual_output, **kwargs}.items()
        }

        if self.evaluation_steps is None:
            # Need to disable validators to allow for both `criteria` and `evaluation_steps` to be set
            with validators.disabled():
                self.evaluation_steps = self._generate_steps(evaluation_params)

        return self._generate_results(evaluation_params)

    def _generate_steps(self, evaluation_params: dict[str, str]) -> list[str]:
        system_prompt = self.generate_steps_system_template.render(
            evaluation_params=", ".join(param for param in evaluation_params),
            criteria=self.criteria,
        )
        user_prompt = self.generate_steps_user_template.render()

        result = self.prompt_driver.run(
            PromptStack(
                messages=[
                    Message(system_prompt, role=Message.SYSTEM_ROLE),
                    Message(user_prompt, role=Message.USER_ROLE),
                ],
                output_schema=STEPS_SCHEMA,
            ),
        ).to_artifact()

        parsed_result = json.loads(result.value)

        return parsed_result["steps"]

    def _generate_results(self, evaluation_params: dict[str, str]) -> tuple[float, str]:
        system_prompt = self.generate_results_system_template.render(
            evaluation_params=", ".join(param for param in evaluation_params),
            evaluation_steps=self.evaluation_steps,
            evaluation_text="\n\n".join(f"{key}: {value}" for key, value in evaluation_params.items()),
        )
        user_prompt = self.generate_results_user_template.render()

        result = self.prompt_driver.run(
            PromptStack(
                messages=[
                    Message(system_prompt, role=Message.SYSTEM_ROLE),
                    Message(user_prompt, role=Message.USER_ROLE),
                ],
                output_schema=RESULTS_SCHEMA,
            ),
        ).to_text()

        parsed_result = json.loads(result)

        # Better to have the LLM deal strictly with integers to avoid ambiguities with floating point precision.
        # We want the user to receive a float, however.
        score = float(parsed_result["score"]) / 10
        reason = parsed_result["reason"]

        return score, reason
