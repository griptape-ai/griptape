In this example we implement a multi-agent Workflow we have a single "Researcher" Agent that conducts research on a topic, and then fans out to multiple "Writer" Agents to write blog posts based on the research.

By splitting up our workloads across multiple Structures, we can parallelize the work and leverage the strengths of each Agent. The Researcher can focus on gathering data and insights, while the Writers can focus on crafting engaging narratives.
Additionally, this architecture opens us up to using services such as [Griptape Cloud](https://www.griptape.ai/cloud) to have each Agent run on a separate machine, allowing us to scale our Workflow as needed.


```python
import json
import os
from pathlib import Path

from griptape.drivers import WebhookEventListenerDriver
from griptape.events import EventListener, FinishStructureRunEvent
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent, Workflow
from griptape.tasks import NoOpTask, StructureRunTask
from griptape.tools import (
    TaskMemoryClient,
    WebScraper,
    WebSearch,
)


def build_researcher():
    """Builds a Researcher Structure."""
    researcher = Agent(
        id="researcher",
        tools=[
            WebSearch(
                google_api_key=os.environ["GOOGLE_API_KEY"],
                google_api_search_id=os.environ["GOOGLE_API_SEARCH_ID"],
                off_prompt=False,
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
                    webhook_url=os.environ["ZAPIER_WEBHOOK_URL"],
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
    # load up the list of writers
    with open(f"{Path(__file__).parent}/writers.json", "r") as f:
        writers = json.loads(f.read())

    # Build the team
    team = Workflow()
    research_task = team.add_task(
        StructureRunTask(
            """Conduct a comprehensive analysis of the latest advancements in AI in 2024.
                Identify key trends, breakthrough technologies, and potential industry impacts.""",
            id="research",
            target_structure=build_researcher(),
        ),
    )
    end_task = team.add_task(NoOpTask())
    team.insert_tasks(
        research_task,
        [
            StructureRunTask(
                """Using insights provided, develop an engaging blog
                post that highlights the most significant AI advancements.
                Your post should be informative yet accessible, catering to a tech-savvy audience.
                Make it sound cool, avoid complex words so it doesn't sound like AI.

                Insights:
                {{ parent_outputs["research"] }}""",
                target_structure=build_writer(
                    role=writer["role"],
                    goal=writer["goal"],
                    backstory=writer["backstory"],
                ),
            )
            for writer in writers
        ],
        end_task,
    )

    team.run()
```

Save this JSON data as `writers.json` in the same directory as the script:
```json
[
    {
        "role": "Tech Content Strategist",
        "goal": "Craft compelling content on tech advancements",
        "backstory": "You are a renowned Content Strategist, known for your insightful and engaging articles. You transform complex concepts into compelling narratives."
    },
    {
        "role": "Travel Adventure Blogger",
        "goal": "Inspire wanderlust with stories of hidden gems and exotic locales",
        "backstory": "With a passport full of stamps, you bring distant cultures and breathtaking scenes to life through vivid storytelling and personal anecdotes."
    },
    {
        "role": "Lifestyle Freelance Writer",
        "goal": "Share practical advice on living a balanced and stylish life",
        "backstory": "From the latest trends in home decor to tips for wellness, your articles help readers create a life that feels both aspirational and attainable."
    },
    {
        "role": "Sports Analyst",
        "goal": "Deliver in-depth analyses and predictions for upcoming games",
        "backstory": "As a former athlete with a deep understanding of various sports, you provide fans with expert insights and game breakdowns."
    },
    {
        "role": "Financial Advisor Columnist",
        "goal": "Educate readers on smart financial strategies and market trends",
        "backstory": "With years of experience in finance, you distill complex financial concepts into easy-to-understand advice for everyday investors."
    },
    {
        "role": "Science Fiction Writer",
        "goal": "Explore futuristic scenarios and expand the boundaries of imagination",
        "backstory": "Your mind is a crucible of futuristic visions and speculative ideas, crafting narratives that question the fabric of reality and possible futures."
    },
    {
        "role": "Health and Wellness Coach",
        "goal": "Promote healthy living through evidence-based practices",
        "backstory": "Combining your expertise in nutrition and fitness with a passion for helping others, you write to inspire and guide readers toward a healthier lifestyle."
    },
    {
        "role": "Political Correspondent",
        "goal": "Provide sharp analysis and comprehensive coverage of political events",
        "backstory": "With a knack for understanding and interpreting political maneuvers, you provide readers with insightful commentary on the current political landscape."
    },
    {
        "role": "Culinary Critic",
        "goal": "Review new restaurants and uncover the best culinary experiences",
        "backstory": "Your palate is your guide as you traverse the world of flavors, sharing your culinary discoveries and restaurant reviews with food enthusiasts."
    },
    {
        "role": "Environmental Activist Writer",
        "goal": "Raise awareness about environmental issues and advocate for sustainable practices",
        "backstory": "As someone deeply committed to the environment, your writings aim to inspire action and change in how people interact with the planet."
    },
    {
        "role": "Historical Biographer",
        "goal": "Illuminate the lives of historical figures with detailed and engaging biographies",
        "backstory": "You delve deep into the past to bring the stories of historical figures to life, connecting their experiences to contemporary lessons."
    }
]
```
