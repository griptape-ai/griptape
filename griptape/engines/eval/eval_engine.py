from __future__ import annotations

import json
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from attrs import Attribute, Factory, define, field, validators

from griptape.common import Message, PromptStack
from griptape.configs import Defaults
from griptape.engines import BaseEvalEngine
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define(kw_only=True)
class EvalEngine(BaseEvalEngine, SerializableMixin):
    class Param(Enum):
        INPUT = "Input"
        ACTUAL_OUTPUT = "Actual Output"
        EXPECTED_OUTPUT = "Expected Output"
        CONTEXT = "Context"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    name: str = field(
        default=Factory(lambda self: self.id, takes_self=True),
        metadata={"serializable": True},
    )
    criteria: Optional[str] = field(default=None, metadata={"serializable": True})
    evaluation_steps: Optional[list[str]] = field(default=None, metadata={"serializable": True})
    prompt_driver: BasePromptDriver = field(default=Factory(lambda: Defaults.drivers_config.prompt_driver))
    evaluation_params: list[EvalEngine.Param] = field(
        default=Factory(lambda: [EvalEngine.Param.INPUT, EvalEngine.Param.ACTUAL_OUTPUT])
    )
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

    @evaluation_params.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_evaluation_params(self, attribute: Attribute, value: list[EvalEngine.Param]) -> None:
        if not value:
            raise ValueError("evaluation_params must not be empty")

        if EvalEngine.Param.INPUT not in value:
            raise ValueError("Input is required in evaluation_params")

        if EvalEngine.Param.ACTUAL_OUTPUT not in value:
            raise ValueError("Actual Output is required in evaluation_params")

    def __attrs_post_init__(self) -> None:
        if self.evaluation_steps is None:
            with validators.disabled():
                self.evaluation_steps = self._generate_steps()

    def evaluate(self, **kwargs) -> tuple[float, str]:
        if not all(key.upper() in EvalEngine.Param.__members__ for key in kwargs):
            raise ValueError("All keys in kwargs must be a member of EvalEngine.Param")

        if EvalEngine.Param.INPUT.name.lower() not in kwargs:
            raise ValueError("Input is required for evaluation")
        if EvalEngine.Param.ACTUAL_OUTPUT.name.lower() not in kwargs:
            raise ValueError("Actual Output is required for evaluation")

        text = "\n\n".join(f"{EvalEngine.Param[key.upper()]}: {value}" for key, value in kwargs.items())

        return self._generate_results(text)

    def _generate_steps(self) -> list[str]:
        system_prompt = self.generate_steps_system_template.render(
            parameters=self.__generate_evaluation_params_str(self.evaluation_params),
            criteria=self.criteria,
        )
        user_prompt = self.generate_steps_user_template.render()

        result = self.prompt_driver.run(
            PromptStack(
                messages=[
                    Message(system_prompt, role=Message.SYSTEM_ROLE),
                    Message(user_prompt, role=Message.USER_ROLE),
                ],
            ),
        ).to_artifact()

        parsed_result = json.loads(result.value)

        return parsed_result["steps"]

    def _generate_results(self, text: str) -> tuple[float, str]:
        system_prompt = self.generate_results_system_template.render(
            parameters=self.__generate_evaluation_params_str(self.evaluation_params),
            evaluation_steps=self.evaluation_steps,
            text=text,
        )
        user_prompt = self.generate_results_user_template.render()

        result = self.prompt_driver.run(
            PromptStack(
                messages=[
                    Message(system_prompt, role=Message.SYSTEM_ROLE),
                    Message(user_prompt, role=Message.USER_ROLE),
                ],
            ),
        ).to_artifact()

        parsed_result = json.loads(result.value)

        score = float(parsed_result["score"]) / 10
        reason = parsed_result["reason"]

        return score, reason

    def __generate_evaluation_params_str(self, evaluation_params: list[EvalEngine.Param]) -> str:
        return ", ".join(param.value for param in evaluation_params)
