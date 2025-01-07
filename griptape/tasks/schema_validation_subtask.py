import jsonschema
from attrs import define, field

from griptape.artifacts import BaseArtifact, JsonArtifact
from griptape.tasks.base_subtask import BaseSubtask


@define()
class SchemaValidationSubtask(BaseSubtask):
    schema: dict = field(kw_only=True)
    _input: JsonArtifact = field(kw_only=True, alias="input")

    @property
    def input(self) -> JsonArtifact:
        return JsonArtifact(self._input)

    @input.setter
    def input(self, value: JsonArtifact) -> None:
        self._input = value

    def try_run(self) -> BaseArtifact:
        jsonschema.validate(self.input.value, self.schema)

        return self.input
