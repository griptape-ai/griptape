import random

from schema import Literal, Optional, Schema

from griptape.artifacts import TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.structures import Agent
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class RandomTool(BaseTool):
    @activity(
        config={
            "description": "Can be used to generate random numbers",
        }
    )
    def generate_rand_num(self) -> TextArtifact:
        """Generate a random number between 0 and 1.

        Returns:
            TextArtifact: The random number as a Text Artifact.
        """
        return TextArtifact(random.random())

    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {
                    Literal("start", description="The start of the rand range, inclusive."): int,
                    Literal("stop", description="The start of the rand range, exclusive."): int,
                }
            ),
        }
    )
    def generate_rand_range(self, start: int, stop: int) -> TextArtifact:
        """Generate a random number between start and stop.

        Args:
            start (int): The starting number.
            stop (int): The ending number.

        Returns:
            TextArtifact: The random number as a Text Artifact.
        """
        return TextArtifact(random.randrange(start, stop))

    @activity(
        config={
            "description": "Can be used to select a random item from a list",
            "schema": Schema(
                {
                    "items": [str],
                }
            ),
        }
    )
    def select_rand_item(self, *, values: dict) -> TextArtifact:
        """Select a random item from a list.

        Args:
            values (dict): The values declared by the schema.

        Returns:
            TextArtifact: The selected item as a Text Artifact.
        """
        items = values["items"]

        return TextArtifact(random.choice(items))

    @activity(
        config={
            "description": "Can be used to sample a list",
            "schema": Schema(
                {
                    "items": [str],
                    Optional("k"): int,
                }
            ),
        }
    )
    def sample_list(self, *, params: dict) -> ListArtifact[TextArtifact]:
        """Shuffle a list.

        Args:
            params (dict): A dictionary containing a key, `values`, which contains the values declared by the schema.

        Returns:
            TextArtifact: The sampled list as a List Artifact of Text Artifacts.
        """
        values = params["values"]

        items = values["items"]
        k = values.get("k", 5)

        sampled = random.sample(items, k)

        return ListArtifact([TextArtifact(item) for item in sampled])


agent = Agent(tools=[RandomTool()])

agent.run("Generate a number between 5 and 10, then generate that many animals, sample 3, then randomly select one.")
