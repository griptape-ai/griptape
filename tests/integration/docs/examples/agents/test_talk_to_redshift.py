import re


class TestTalkToRedshift:
    """
    https://docs.griptape.ai/en/latest/examples/talk-to-redshift/
    """

    def test_talk_to_redshift(self):
        import boto3
        import os
        from griptape.drivers import AmazonRedshiftSqlDriver
        from griptape.loaders import SqlLoader
        from griptape.rules import Ruleset, Rule
        from griptape.structures import Agent
        from griptape.tools import SqlClient

        session = boto3.Session(region_name=os.getenv("AWS_DEFAULT_REGION"))

        sql_loader = SqlLoader(
            sql_driver=AmazonRedshiftSqlDriver(
                database=os.getenv("REDSHIFT_DATABASE"),
                session=session,
                cluster_identifier=os.getenv("REDSHIFT_CLUSTER_IDENTIFIER"),
            )
        )

        sql_tool = SqlClient(
            sql_loader=sql_loader,
            table_name="people",
            table_description="contains information about tech industry professionals",
            engine_name="redshift",
        )

        agent = Agent(
            tools=[sql_tool],
            rulesets=[
                Ruleset(
                    name="HumansOrg Agent",
                    rules=[
                        Rule(
                            "Act and introduce yourself as a HumansOrg, Inc. support agent"
                        ),
                        Rule(
                            "Your main objective is to help with finding information about people"
                        ),
                        Rule(
                            "Only use information about people from the sources available to you"
                        ),
                    ],
                )
            ],
        )

        result = agent.run("Tell me about John Doe")

        assert result.output is not None
        assert re.search("coder", result.output.to_text(), re.IGNORECASE)
