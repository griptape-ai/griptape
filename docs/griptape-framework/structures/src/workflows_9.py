from griptape.rules import Rule
from griptape.structures import Workflow
from griptape.tasks import PromptTask

workflow = Workflow(
    rules=[Rule("output a single lowercase word")],
)

animal_task = PromptTask("Name an animal", id="animal")
adjective_task = PromptTask("Describe {{ parent_outputs['animal'] }} with an adjective", id="adjective")
color_task = PromptTask("Describe {{ parent_outputs['animal'] }} with a color", id="color")
new_animal_task = PromptTask("Name an animal described as: \n{{ parents_output_text }}", id="new-animal")

# The following workflow runs animal_task, then (adjective_task, and color_task)
# in parallel, then finally new_animal_task.
#
# In other words, the output of animal_task is passed to both adjective_task and color_task
# and the outputs of adjective_task and color_task are then passed to new_animal_task.
workflow.add_task(animal_task)
workflow.add_task(new_animal_task)
workflow.insert_tasks(animal_task, [adjective_task, color_task], new_animal_task)

workflow.run()
