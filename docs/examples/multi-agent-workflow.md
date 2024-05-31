In this example we implement a multi-agent Workflow. We have a single "Researcher" Agent that conducts research on a topic, and then fans out to multiple "Writer" Agents to write blog posts based on the research.

By splitting up our workloads across multiple Structures, we can parallelize the work and leverage the strengths of each Agent. The Researcher can focus on gathering data and insights, while the Writers can focus on crafting engaging narratives.
Additionally, this architecture opens us up to using services such as [Griptape Cloud](https://www.griptape.ai/cloud) to have each Agent run on a separate machine, allowing us to scale our Workflow as needed 🤯.


```python
import os

from griptape.drivers import WebhookEventListenerDriver, LocalStructureRunDriver
from griptape.events import EventListener, FinishStructureRunEvent
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent, Workflow
from griptape.tasks import PromptTask, StructureRunTask
from griptape.tools import (
    TaskMemoryClient,
    WebScraper,
    WebSearch,
)

WRITERS = [
    {
        "role": "Travel Adventure Blogger",
        "goal": "Inspire wanderlust with stories of hidden gems and exotic locales",
        "backstory": "With a passport full of stamps, you bring distant cultures and breathtaking scenes to life through vivid storytelling and personal anecdotes.",
    },
    {
        "role": "Lifestyle Freelance Writer",
        "goal": "Share practical advice on living a balanced and stylish life",
        "backstory": "From the latest trends in home decor to tips for wellness, your articles help readers create a life that feels both aspirational and attainable.",
    },
]


def build_researcher():
    """Builds a Researcher Structure."""
    researcher = Agent(
        id="researcher",
        tools=[
            WebSearch(
                google_api_key=os.environ["GOOGLE_API_KEY"],
                google_api_search_id=os.environ["GOOGLE_API_SEARCH_ID"],
            ),
            WebScraper(
                off_prompt=True,
            ),
            TaskMemoryClient(off_prompt=False),
        ],
        rulesets=[
            Ruleset(
                name="Position",
                rules=[
                    Rule(
                        value="Lead Research Analyst",
                    )
                ],
            ),
            Ruleset(
                name="Objective",
                rules=[
                    Rule(
                        value="Discover innovative advancements in artificial intelligence and data analytics",
                    )
                ],
            ),
            Ruleset(
                name="Background",
                rules=[
                    Rule(
                        value="""You are part of a prominent technology research institute.
                        Your speciality is spotting new trends.
                        You excel at analyzing intricate data and delivering practical insights."""
                    )
                ],
            ),
            Ruleset(
                name="Desired Outcome",
                rules=[
                    Rule(
                        value="Comprehensive analysis report in list format",
                    )
                ],
            ),
        ],
    )

    return researcher


def build_writer(role: str, goal: str, backstory: str):
    """Builds a Writer Structure.

    Args:
        role: The role of the writer.
        goal: The goal of the writer.
        backstory: The backstory of the writer.
    """
    writer = Agent(
        id=role.lower().replace(" ", "_"),
        event_listeners=[
            EventListener(
                event_types=[FinishStructureRunEvent],
                driver=WebhookEventListenerDriver(
                    webhook_url=os.environ["WEBHOOK_URL"],
                ),
            )
        ],
        rulesets=[
            Ruleset(
                name="Position",
                rules=[
                    Rule(
                        value=role,
                    )
                ],
            ),
            Ruleset(
                name="Objective",
                rules=[
                    Rule(
                        value=goal,
                    )
                ],
            ),
            Ruleset(
                name="Backstory",
                rules=[Rule(value=backstory)],
            ),
            Ruleset(
                name="Desired Outcome",
                rules=[
                    Rule(
                        value="Full blog post of at least 4 paragraphs",
                    )
                ],
            ),
        ],
    )

    return writer


if __name__ == "__main__":
    # Build the team
    team = Workflow()
    research_task = team.add_task(
        StructureRunTask(
            (
                """Perform a detailed examination of the newest developments in AI as of 2024.
                Pinpoint major trends, breakthroughs, and their implications for various industries.""",
            ),
            id="research",
            driver=LocalStructureRunDriver(
                structure_factory_fn=build_researcher,
            ),
        ),
    )
    end_task = team.add_task(
        PromptTask(
            'State "All Done!"',
        )
    )
    team.insert_tasks(
        research_task,
        [
            StructureRunTask(
                (
                    """Using insights provided, develop an engaging blog
                post that highlights the most significant AI advancements.
                Your post should be informative yet accessible, catering to a tech-savvy audience.
                Make it sound cool, avoid complex words so it doesn't sound like AI.

                Insights:
                {{ parent_outputs["research"] }}""",
                ),
                driver=LocalStructureRunDriver(
                    structure_factory_fn=lambda: build_writer(
                        role=writer["role"],
                        goal=writer["goal"],
                        backstory=writer["backstory"],
                    )
                ),
            )
            for writer in WRITERS
        ],
        end_task,
    )

    team.run()
```
