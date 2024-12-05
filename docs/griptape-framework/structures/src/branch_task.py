from griptape.artifacts import InfoArtifact
from griptape.loaders import ImageLoader
from griptape.structures import Workflow
from griptape.tasks import BranchTask, PromptTask


def on_run(task: BranchTask) -> InfoArtifact:
    if "hot dog" in task.input.value:
        return InfoArtifact("hot_dog")
    else:
        return InfoArtifact("not_hot_dog")


image_artifact = ImageLoader().load("tests/resources/mountain.png")

workflow = Workflow(
    tasks=[
        PromptTask(["What is in this image?", image_artifact], child_ids=["branch"]),
        BranchTask(
            "{{ parents_output_text }}",
            on_run=on_run,
            id="branch",
            child_ids=["hot_dog", "not_hot_dog"],
        ),
        PromptTask("Tell me about hot dogs", id="hot_dog"),
        PromptTask("Tell me about anything but hotdogs", id="not_hot_dog"),
    ]
)

workflow.run()
