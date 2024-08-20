from griptape.rules import Rule
from griptape.structures import Workflow
from griptape.tasks import PromptTask

workflow = Workflow(
    tasks=[
        PromptTask("Name an animal", id="animal"),
        PromptTask("Describe {{ parent_outputs['animal'] }} with an adjective", id="adjective", parent_ids=["animal"]),
        PromptTask("Name a {{ parent_outputs['adjective'] }} animal", id="new-animal", parent_ids=["adjective"]),
    ],
    rules=[Rule("output a single lowercase word")],
)

workflow.run()
