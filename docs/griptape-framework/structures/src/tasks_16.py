import os

from griptape.drivers.structure_run.local import LocalStructureRunDriver
from griptape.drivers.web_search.google import GoogleWebSearchDriver
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask
from griptape.tools import (
    PromptSummaryTool,
    WebScraperTool,
    WebSearchTool,
)


def build_researcher() -> Agent:
    return Agent(
        tools=[
            WebSearchTool(
                web_search_driver=GoogleWebSearchDriver(
                    api_key=os.environ["GOOGLE_API_KEY"],
                    search_id=os.environ["GOOGLE_API_SEARCH_ID"],
                ),
            ),
            WebScraperTool(
                off_prompt=True,
            ),
            PromptSummaryTool(off_prompt=False),
        ],
        rulesets=[
            Ruleset(
                name="Position",
                rules=[
                    Rule(
                        value="Senior Research Analyst",
                    )
                ],
            ),
            Ruleset(
                name="Objective",
                rules=[
                    Rule(
                        value="Uncover cutting-edge developments in AI and data science",
                    )
                ],
            ),
            Ruleset(
                name="Background",
                rules=[
                    Rule(
                        value="""You work at a leading tech think tank.,
                        Your expertise lies in identifying emerging trends.
                        You have a knack for dissecting complex data and presenting actionable insights."""
                    )
                ],
            ),
            Ruleset(
                name="Desired Outcome",
                rules=[
                    Rule(
                        value="Full analysis report in bullet points",
                    )
                ],
            ),
        ],
    )


def build_writer() -> Agent:
    return Agent(
        input="Instructions: {{args[0]}}\nContext: {{args[1]}}",
        rulesets=[
            Ruleset(
                name="Position",
                rules=[
                    Rule(
                        value="Tech Content Strategist",
                    )
                ],
            ),
            Ruleset(
                name="Objective",
                rules=[
                    Rule(
                        value="Craft compelling content on tech advancements",
                    )
                ],
            ),
            Ruleset(
                name="Backstory",
                rules=[
                    Rule(
                        value="""You are a renowned Content Strategist, known for your insightful and engaging articles.
                        You transform complex concepts into compelling narratives."""
                    )
                ],
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


team = Pipeline(
    tasks=[
        StructureRunTask(
            (
                """Perform a detailed examination of the newest developments in AI as of 2024.
                Pinpoint major trends, breakthroughs, and their implications for various industries.""",
            ),
            structure_run_driver=LocalStructureRunDriver(create_structure=build_researcher),
        ),
        StructureRunTask(
            (
                """Utilize the gathered insights to craft a captivating blog
                article showcasing the key AI innovations.
                Ensure the content is engaging yet straightforward, appealing to a tech-aware readership.
                Keep the tone appealing and use simple language to make it less technical.""",
                "{{parent_output}}",
            ),
            structure_run_driver=LocalStructureRunDriver(create_structure=build_writer),
        ),
    ],
)

team.run()
