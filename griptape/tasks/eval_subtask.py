import json
import logging

from attrs import define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import PromptStack
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.engines import EvalEngine
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.tasks.base_subtask import BaseSubtask
from griptape.tasks.prompt_task import PromptTask
from griptape.utils import with_contextvars
from griptape.utils.futures import execute_futures_dict

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class EvalSubtask(BaseSubtask, FuturesExecutorMixin):
    _input: BaseArtifact = field(alias="input")
    threshold: float = field(default=0.5)

    @property
    def input(self) -> BaseArtifact:
        return self._input

    @property
    def user_input(self) -> BaseArtifact:
        return self.origin_task.input

    @property
    def actual_output(self) -> BaseArtifact:
        return self.input

    @property
    def eval_engines(self) -> list[EvalEngine]:
        if isinstance(self.origin_task, PromptTask):
            rulesets = self.origin_task.rulesets

            return [ruleset.eval_engine for ruleset in rulesets if ruleset.eval_engine is not None]
        else:
            return []

    def before_run(self) -> None:
        logger.info(
            "%s %s\nInput: %s\n\nOutput: %s\n\nEvals: %s",
            self.__class__.__name__,
            self.id,
            self.user_input,
            self.actual_output,
            self._eval_engines_to_json(self.eval_engines),
        )

    def should_run(self) -> bool:
        return len(self.eval_engines) > 0

    def try_run(self) -> BaseArtifact:
        eval_results = execute_futures_dict(
            {
                eval_engine.name: self.futures_executor.submit(
                    with_contextvars(eval_engine.evaluate),
                    input=self.user_input,
                    actual_output=self.actual_output,
                )
                for eval_engine in self.eval_engines
            },
        )

        if all(score >= self.threshold for score, _ in eval_results.values()):
            return TextArtifact(self.actual_output.value, meta={"eval_results": eval_results})
        else:
            return ListArtifact(
                [
                    InfoArtifact(
                        reason,
                        meta={"eval_engine_name": eval_engine_name, "score": score, "reason": reason},
                    )
                    for eval_engine_name, (score, reason) in eval_results.items()
                ]
            )

    def after_run(self) -> None:
        logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.to_text())

    def to_text(self) -> str:
        output = self.output

        if isinstance(output, ListArtifact):
            return json.dumps(
                [
                    {
                        "name": artifact.meta["eval_engine_name"],
                        "score": artifact.meta["score"],
                        "reason": artifact.meta["reason"],
                    }
                    for artifact in output
                ],
                indent=2,
            )
        elif isinstance(output, TextArtifact):
            return json.dumps(
                [
                    {
                        "name": eval_engine_name,
                        "score": score,
                        "reason": reason,
                    }
                    for eval_engine_name, (score, reason) in output.meta["eval_results"].items()
                ],
                indent=2,
            )
        else:
            return ""

    def add_to_prompt_stack(self, prompt_driver: BasePromptDriver, prompt_stack: PromptStack) -> None:
        prompt_stack.add_assistant_message(self.input.to_text())
        prompt_stack.add_user_message(self.output.to_text())

    def _eval_engines_to_json(self, eval_engines: list[EvalEngine]) -> str:
        return json.dumps(
            [
                {
                    "name": eval_engine.name,
                    "evaluation_steps": eval_engine.evaluation_steps,
                }
                for eval_engine in eval_engines
            ],
            indent=2,
        )
