from griptape.rules import Rule
from griptape.structures import Workflow
from griptape.tasks import PromptTask

animal_task = PromptTask("Name an animal", id="animal")
adjective_task = PromptTask("Describe {{ parent_outputs['animal'] }} with an adjective", id="adjective")
new_animal_task = PromptTask("Name a {{ parent_outputs['adjective'] }} animal", id="new-animal")

animal_task.add_child(adjective_task)
adjective_task.add_child(new_animal_task)

workflow = Workflow(
    tasks=[animal_task, adjective_task, new_animal_task],
    rules=[Rule("output a single lowercase word")],
)

workflow.run()
