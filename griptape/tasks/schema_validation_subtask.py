import json
import logging

from attrs import define, field
from schema import Schema, SchemaError

from griptape.artifacts import BaseArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.configs import Defaults
from griptape.tasks import BaseSubtask, BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define()
class SchemaValidationSubtask(BaseSubtask):
    schema: Schema = field(kw_only=True)

    def before_run(self) -> None:
        parts = [
            f"{self.__class__.__name__} {self.id}",
            f"\nSchema: {json.dumps(self.schema.json_schema('Schema'), indent=2)}",
            f"\nInput: {self.input.to_text()}",
        ]
        logger.info("".join(parts))

    def attach_to(self, parent_task: BaseTask) -> None:
        super().attach_to(parent_task)

        # If we can successfully parse and validate when attaching
        # we don't need to run the subtask
        output = self._parse_and_validate_input()

        if not isinstance(output, ErrorArtifact):
            self.output = output

    def try_run(self) -> BaseArtifact:
        if self.output is None:
            return self._parse_and_validate_input()
        else:
            return self.output

    def after_run(self) -> None:
        logger.info("Output: %s", self.output)

    def _parse_and_validate_input(self) -> BaseArtifact:
        try:
            parsed_input = json.loads(self.input.value)
            self.schema.validate(parsed_input)

            return self.input
        except (SchemaError, json.JSONDecodeError) as e:
            return ErrorArtifact(e)
