import os

import boto3

from griptape.drivers.sql.amazon_redshift import AmazonRedshiftSqlDriver
from griptape.loaders import SqlLoader
from griptape.structures import Agent
from griptape.tools import SqlTool

session = boto3.Session()

sql_loader = SqlLoader(
    sql_driver=AmazonRedshiftSqlDriver(
        database=os.environ["REDSHIFT_DATABASE"],
        session=session,
        cluster_identifier=os.environ["REDSHIFT_CLUSTER_IDENTIFIER"],
    )
)

sql_tool = SqlTool(
    sql_loader=sql_loader,
    table_name="people",
    table_description="contains information about tech industry professionals",
    engine_name="redshift",
)

agent = Agent(tools=[sql_tool])
agent.run("SELECT * FROM people;")
