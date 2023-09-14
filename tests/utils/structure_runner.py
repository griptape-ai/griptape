import re
from textwrap import dedent
from json import loads
from griptape.rules import Ruleset, Rule

OUTPUT_RULESET = Ruleset(
    name="Output Format",
    rules=[
        Rule(
            value=dedent(
                """Your answer MUST be the following format: 
                {
                    "task_output": "<task output>",
                    "task_result": "<success|failure>",
                }
                """
            )
        )
    ],
)


def run_structure(structure, prompt):
    result = structure.run(prompt)
    response_matches = re.findall(r"[^{]*({.*})", result.output.to_text(), re.DOTALL)
    if response_matches:
        return loads(response_matches[0], strict=False)
    raise ValueError("No response found")
