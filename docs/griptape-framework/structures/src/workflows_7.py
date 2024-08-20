from griptape.rules import Rule
from griptape.structures import Workflow
from griptape.tasks import PromptTask

workflow = Workflow(
    rules=[Rule("output a single lowercase word")],
)

animal_task = PromptTask("Name an animal", id="animal", structure=workflow)
adjective_task = PromptTask(
    "Describe {{ parent_outputs['animal'] }} with an adjective", id="adjective", structure=workflow
)
new_animal_task = PromptTask("Name a {{ parent_outputs['adjective'] }} animal", id="new-animal", structure=workflow)

adjective_task.add_parent(animal_task)
adjective_task.add_child(new_animal_task)

workflow.run()
