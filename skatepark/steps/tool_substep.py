from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING, Optional
from attr import define, field
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from skatepark.artifacts import TextOutput, ErrorOutput
from skatepark.steps import PromptStep
from griptape.core import BaseTool
from skatepark.utils import J2

if TYPE_CHECKING:
    from skatepark.artifacts import StructureArtifact
    from skatepark.steps import BaseToolStep


@define
class ToolSubstep(PromptStep):
    THOUGHT_PATTERN = r"^Thought:\s*(.*)$"
    ACTION_PATTERN = r"^Action:\s*({.*})$"
    OUTPUT_PATTERN = r"^Output:\s?([\s\S]*)$"
    INVALID_ACTION_ERROR_MSG = f"invalid action input, try again"

    tool_step_id: Optional[str] = field(default=None, kw_only=True)
    thought: Optional[str] = field(default=None, kw_only=True)
    tool_name: Optional[str] = field(default=None, kw_only=True)
    tool_action: Optional[str] = field(default=None, kw_only=True)
    tool_value: Optional[str] = field(default=None, kw_only=True)

    _tool: Optional[BaseTool] = None

    def attach(self, tool_step: BaseToolStep):
        self.tool_step_id = tool_step.id
        self.structure = tool_step.structure
        self.__init_from_prompt(self.render_prompt())

    @property
    def tool_step(self) -> Optional[BaseToolStep]:
        return self.structure.find_step(self.tool_step_id)

    @property
    def parents(self) -> list[ToolSubstep]:
        return [self.tool_step.find_substep(parent_id) for parent_id in self.parent_ids]

    @property
    def children(self) -> list[ToolSubstep]:
        return [self.tool_step.find_substep(child_id) for child_id in self.child_ids]

    def before_run(self) -> None:
        self.structure.logger.info(f"Substep {self.id}\n{self.render_prompt()}")

    def run(self) -> StructureArtifact:
        try:
            if self.tool_name == "error":
                self.output = ErrorOutput(self.tool_value, step=self)
            else:
                if self._tool:
                    observation = self.structure.tool_loader.executor.execute(
                        getattr(self._tool, self.tool_action),
                        self.tool_value.encode()
                    ).decode()
                else:
                    observation = "tool not found"

                self.output = TextOutput(observation)
        except Exception as e:
            self.structure.logger.error(f"Substep {self.id}\n{e}", exc_info=True)

            self.output = ErrorOutput(str(e), exception=e, step=self)
        finally:
            return self.output

    def after_run(self) -> None:
        self.structure.logger.info(f"Substep {self.id}\nObservation: {self.output.value}")

    def render(self) -> str:
        return J2("prompts/steps/tool/substep.j2").render(
            substep=self
        )

    def add_child(self, child: ToolSubstep) -> ToolSubstep:
        if child.id not in self.child_ids:
            self.child_ids.append(child.id)

        if self.id not in child.parent_ids:
            child.parent_ids.append(self.id)

        return child

    def add_parent(self, parent: ToolSubstep) -> ToolSubstep:
        if parent.id not in self.parent_ids:
            self.parent_ids.append(parent.id)

        if self.id not in parent.child_ids:
            parent.child_ids.append(self.id)

        return parent

    def __init_from_prompt(self, value: str) -> None:
        thought_matches = re.findall(self.THOUGHT_PATTERN, value, re.MULTILINE)
        action_matches = re.findall(self.ACTION_PATTERN, value, re.MULTILINE)
        output_matches = re.findall(self.OUTPUT_PATTERN, value, re.MULTILINE)

        if self.thought is None and len(thought_matches) > 0:
            self.thought = thought_matches[-1]

        if len(action_matches) > 0:
            try:
                parsed_value = ast.literal_eval(action_matches[-1])

                # Load the tool name; throw exception if the key is not present
                if self.tool_name is None:
                    self.tool_name = parsed_value["tool"]

                # Load the tool action; throw exception if the key is not present
                if self.tool_action is None:
                    self.tool_action = parsed_value["action"]

                # Load the tool itself
                if self.tool_name:
                    self._tool = self.tool_step.find_tool(self.tool_name)

                # Validate input based on tool schema
                if self._tool:
                    validate(
                        instance={
                            "value": parsed_value["value"]
                        },
                        schema=self._tool.action_schema(getattr(self._tool, self.tool_action))
                    )

                # Load optional input value; don't throw exceptions if key is not present
                if self.tool_value is None:
                    self.tool_value = str(parsed_value.get("value"))

            except SyntaxError as e:
                self.structure.logger.error(f"Step {self.tool_step.id}\nSyntax error: {e}")

                self.tool_name = "error"
                self.tool_value = f"syntax error: {e}"
            except ValidationError as e:
                self.structure.logger.error(f"Step {self.tool_step.id}\nInvalid JSON: {e}")

                self.tool_name = "error"
                self.tool_value = f"JSON validation error: {e}"
            except Exception as e:
                self.structure.logger.error(f"Step {self.tool_step.id}\nError parsing tool action: {e}")

                self.tool_name = "error"
                self.tool_value = f"error: {self.INVALID_ACTION_ERROR_MSG}"

        if self.output is None and len(output_matches) > 0:
            self.output = TextOutput(output_matches[-1])
