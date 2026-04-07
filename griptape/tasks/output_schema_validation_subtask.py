from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Callable, Union

from attrs import Factory, define, field
from pydantic import BaseModel, TypeAdapter, ValidationError
from schema import Schema, SchemaError

from griptape.artifacts import BaseArtifact, ErrorArtifact, JsonArtifact, ModelArtifact
from griptape.configs import Defaults
from griptape.tasks import BaseTask
from griptape.tasks.base_subtask import BaseSubtask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.common import PromptStack
    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class OutputSchemaValidationSubtask(BaseSubtask):
    _input: BaseArtifact = field(alias="input")
    output_schema: Union[Schema, type[BaseModel]] = field(kw_only=True)
    structured_output_strategy: StructuredOutputStrategy = field(
        default="rule", kw_only=True, metadata={"serializable": True}
    )
    generate_assistant_subtask_template: Callable[[OutputSchemaValidationSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_assistant_subtask_template, takes_self=True),
        kw_only=True,
    )
    generate_user_subtask_template: Callable[[OutputSchemaValidationSubtask], str] = field(
        default=Factory(lambda self: self.default_generate_user_subtask_template, takes_self=True),
        kw_only=True,
    )
    _validation_errors: str | None = field(default=None, init=False)

    @property
    def input(self) -> BaseArtifact:
        return self._input

    @input.setter
    def input(self, value: BaseArtifact) -> None:
        self._input = value

    @property
    def validation_errors(self) -> str | None:
        return self._validation_errors

    def attach_to(self, parent_task: BaseTask) -> None:
        super().attach_to(parent_task)
        try:
            # With `native` or `rule` strategies, the output will be a json string that can be parsed.
            # With the `tool` strategy, the output will already be a `JsonArtifact`.
            if self.structured_output_strategy in ("native", "rule"):
                value_to_validate = (
                    self.input.value if isinstance(self.input.value, str) else json.dumps(self.input.value)
                )
                if isinstance(self.output_schema, Schema):
                    self.output_schema.validate(json.loads(value_to_validate))
                    self.output = JsonArtifact(self.input.value)
                else:
                    model = TypeAdapter(self.output_schema).validate_json(value_to_validate)
                    self.output = ModelArtifact(model)
            else:
                self.output = self.input
        except SchemaError as e:
            self._validation_errors = str(e)
        except ValidationError as e:
            self._validation_errors = str(e.errors())

    def before_run(self) -> None:
        logger.info("%s Validating: %s", self.__class__.__name__, self.input.value)

    def try_run(self) -> BaseArtifact:
        if self._validation_errors is None:
            return self._input
        return ErrorArtifact(
            value=f"Validation error: {self._validation_errors}",
        )

    def after_run(self) -> None:
        if self._validation_errors is None:
            logger.info("%s Validation successful", self.__class__.__name__)
        else:
            logger.error("%s Validation error: %s", self.__class__.__name__, self._validation_errors)

    def add_to_prompt_stack(self, stack: PromptStack) -> None:
        if self.output is None:
            return
        stack.add_assistant_message(self.generate_assistant_subtask_template(self))
        stack.add_user_message(self.generate_user_subtask_template(self))

    def default_generate_assistant_subtask_template(self, subtask: OutputSchemaValidationSubtask) -> str:
        return J2("tasks/prompt_task/assistant_output_schema_validation_subtask.j2").render(
            subtask=subtask,
        )

    def default_generate_user_subtask_template(self, subtask: OutputSchemaValidationSubtask) -> str:
        return J2("tasks/prompt_task/user_output_schema_validation_subtask.j2").render(
            subtask=subtask,
        )
