import os

import boto3

from griptape.drivers import AmazonRedshiftSqlDriver
from griptape.loaders import SqlLoader
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.tools import FileManager, SqlClient
from griptape.utils import Chat

session = boto3.Session()

sql_loader = SqlLoader(
    sql_driver=AmazonRedshiftSqlDriver(
        database=os.environ["REDSHIFT_DATABASE"],
        session=session,
        cluster_identifier=os.environ["REDSHIFT_CLUSTER_IDENTIFIER"],
    )
)

sql_tool = SqlClient(
    sql_loader=sql_loader,
    table_name="people",
    table_description="contains information about tech industry professionals",
    engine_name="redshift",
)

agent = Agent(
    tools=[sql_tool, FileManager()],
    rulesets=[
        Ruleset(
            name="HumansOrg Agent",
            rules=[
                Rule("Act and introduce yourself as a HumansOrg, Inc. support agent"),
                Rule("Your main objective is to help with finding information about people"),
                Rule("Only use information about people from the sources available to you"),
            ],
        )
    ],
)

Chat(agent).start()
