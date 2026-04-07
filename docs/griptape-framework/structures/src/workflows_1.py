from griptape.structures import Workflow
from griptape.tasks import PromptTask
from griptape.utils import StructureVisualizer

world_task = PromptTask(
    "Create a fictional world based on the following key words {{ keywords|join(', ') }}",
    context={"keywords": ["fantasy", "ocean", "tidal lock"]},
    id="world",
)


def character_task(task_id: str, character_name: str) -> PromptTask:
    return PromptTask(
        "Based on the following world description create a character named {{ name }}:\n{{ parent_outputs['world'] }}",
        context={"name": character_name},
        id=task_id,
        parent_ids=["world"],
    )


scotty_task = character_task("scotty", "Scotty")
annie_task = character_task("annie", "Annie")

story_task = PromptTask(
    "Based on the following description of the world and characters, write a short story:\n{{ parent_outputs['world'] }}\n{{ parent_outputs['scotty'] }}\n{{ parent_outputs['annie'] }}",
    id="story",
    parent_ids=["world", "scotty", "annie"],
)

workflow = Workflow(tasks=[world_task, story_task, scotty_task, annie_task, story_task])

print(StructureVisualizer(workflow).to_url())

workflow.run()
