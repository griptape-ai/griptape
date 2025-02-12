import random

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.structures import Workflow
from griptape.tasks import CodeExecutionTask, PromptTask
from griptape.utils import StructureVisualizer


# Define a function that will generate a fantasy title by combining inputs
def generate_title(task: CodeExecutionTask) -> BaseArtifact:
    # Make sure this is part of a valid structure
    structure = task.structure
    if structure is None:
        raise ValueError("Task must be part of a structure to run")

    # Retrieve outputs from previous tasks using their task IDs
    hero = structure.find_task("hero").output  # Gets the hero name from first prompt
    setting = structure.find_task("setting").output  # Gets the setting from second prompt

    # List of epic titles to randomly choose from
    titles = ["the Brave", "the Shadow", "the Flame", "the Eternal", "the Cursed"]
    # Combine the hero name, random title, and setting into a full title
    generated_title = f"{hero} {random.choice(titles)} of {setting}"

    # Return the generated title as a TextArtifact that can be used by other tasks
    return TextArtifact(generated_title)


# Create a new workflow to organize our tasks
workflow = Workflow()

# Add a sequence of connected tasks to the workflow
workflow.add_tasks(
    # First task: Prompt for a hero name
    # The child_ids parameter connects this to the generate_title task
    PromptTask("Name a fantasy hero (e.g., 'Eldric')", id="hero", child_ids=["generate_title"]),
    # Second task: Prompt for a setting
    # Also connected to generate_title task
    PromptTask(
        "Describe a mystical setting in a couple sentences (e.g., 'the Shattered Isles')",
        id="setting",
        child_ids=["generate_title"],
    ),
    # Third task: Execute our custom code to generate the title
    # The on_run parameter specifies which function to execute
    CodeExecutionTask(on_run=generate_title, id="generate_title", child_ids=["story"]),
    # Fourth task: Prompt for a story using the generated title
    # {{ parent_outputs['generate_title'] }} references the output from the previous task
    PromptTask(
        "Write a brief, yet heroic tale about {{ parent_outputs['generate_title'] }}. ",
        id="story",
    ),
)

# Visualize the workflow structure (helpful for debugging)
print(StructureVisualizer(workflow).to_url())

# Execute the entire workflow
workflow.run()
