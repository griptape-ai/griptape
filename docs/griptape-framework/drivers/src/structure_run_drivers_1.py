from griptape.drivers import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask


def build_joke_teller() -> Agent:
    joke_teller = Agent(
        rules=[
            Rule(
                value="You are very funny.",
            )
        ],
    )

    return joke_teller


def build_joke_rewriter() -> Agent:
    joke_rewriter = Agent(
        rules=[
            Rule(
                value="You are the editor of a joke book. But you only speak in riddles",
            )
        ],
    )

    return joke_rewriter


joke_coordinator = Pipeline(
    tasks=[
        StructureRunTask(
            driver=LocalStructureRunDriver(
                structure_factory_fn=build_joke_teller,
            ),
        ),
        StructureRunTask(
            ("Rewrite this joke: {{ parent_output }}",),
            driver=LocalStructureRunDriver(
                structure_factory_fn=build_joke_rewriter,
            ),
        ),
    ]
)

joke_coordinator.run("Tell me a joke")
