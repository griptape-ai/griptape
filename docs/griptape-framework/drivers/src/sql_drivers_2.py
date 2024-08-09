import os

import boto3

from griptape.drivers import AmazonRedshiftSqlDriver

session = boto3.Session()

driver = AmazonRedshiftSqlDriver(
    database=os.environ["REDSHIFT_DATABASE"],
    session=session,
    cluster_identifier=os.environ["REDSHIFT_CLUSTER_IDENTIFIER"],
)

driver.execute_query("select * from people;")
