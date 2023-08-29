import json
from typing import Optional
import schema
from attr import define, field
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from schema import Schema, Literal
from griptape import utils
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.tasks import PromptTask
from griptape.tools import BaseTool
from griptape.utils import J2, remove_null_values_in_dict_recursively, ActivityMixin


@define
class ToolTask(PromptTask):
    TOOL_SCHEMA = Schema(
        description="Tools have name, activity, and input value.",
        schema={
            Literal(
                "name",
                description="Tool name"
            ): str,
            Literal(
                "activity",
                description="Tool activity"
            ): str,
            schema.Optional(
                Literal(
                    "input",
                    description="Optional tool activity input object"
                )
            ): dict
        }
    )

    tool: BaseTool = field(kw_only=True)
    tool_activity: Optional[str] = field(default=None, kw_only=True)
    tool_input: Optional[dict] = field(default=None, kw_only=True)

    def default_system_template_generator(self, _: PromptTask) -> str:
        tool_schema = utils.minify_json(
            json.dumps(
                self.TOOL_SCHEMA.json_schema("ToolSchema")
            )
        )

        return J2("tasks/tool_task/system.j2").render(
            rulesets=self.structure.rulesets,
            tool_schema=tool_schema,
            tool=J2("tasks/partials/_tool.j2").render(tool=self.tool)
        )

    def run(self) -> TextArtifact:
        output = self.active_driver().run(self.prompt_stack).value

        try:
            tool_object: dict = json.loads(output)

            validate(
                instance=tool_object,
                schema=self.TOOL_SCHEMA.schema
            )

            self.tool_activity = tool_object["activity"]

            # Load optional input value; don't throw exceptions if key is not present
            if "input" in tool_object:
                # The schema library has a bug, where something like `Or(str, None)` doesn't get
                # correctly translated into JSON schema. For some optional input fields LLMs sometimes
                # still provide null value, which trips up the validator. The temporary solution that
                # works is to strip all key-values where value is null.
                self.tool_input = remove_null_values_in_dict_recursively(tool_object["input"])

            self.__validate_tool_input(self.tool_input)

            self.output = self.tool.execute(getattr(self.tool, self.tool_activity), self)

            return self.output
        except SyntaxError as e:
            self.output = ErrorArtifact(f"syntax error: {e}")
        except ValidationError as e:
            self.output = ErrorArtifact(f"Action JSON validation error: {e}")
        except Exception as e:
            self.output = ErrorArtifact(f"Action input parsing error: {e}")
        finally:
            return self.output

    def __validate_tool_input(self, tool_input: dict) -> None:
        activity_schema = self.tool.activity_schema(getattr(self.tool, self.tool_activity))

        if activity_schema:
            validate(
                instance=tool_input,
                schema=activity_schema
            )
