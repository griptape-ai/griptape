import time
from typing import Optional
import boto3
from griptape.drivers import BaseSqlDriver
from attr import define, field


@define
class AwsRedshiftSqlDriver(BaseSqlDriver):
    database: str = field(kw_only=True)
    region_name: str = field(default="us-east-1", kw_only=True)
    wait_sec: float = field(default=0.3, kw_only=True)
    client = field(init=False)

    def __attrs_post_init__(self):
        self.client = boto3.client(
            "redshift-data", region_name=self.region_name
        )

    def execute_query(self, query: str) -> Optional[list[BaseSqlDriver.RowResult]]:
        response = self.client.execute_statement(
            Sql=query,
            Database=self.database
        )
        response_id = response["Id"]

        statement = self.client.describe_statement(Id=response_id)

        while statement["Status"] == "PICKED":
            time.sleep(self.wait_sec)

            statement = self.client.describe_statement(Id=response_id)

        if statement["Status"] == "FINISHED":
            statement_result = self.client.get_statement_result(Id=response_id)
            results = statement_result.get("Records", [])

            while "NextToken" in statement_result:
                statement_result = self.client.get_statement_result(
                    Id=response_id, NextToken=statement_result["NextToken"]
                )
                results = results + response.get("Records", [])

            return [BaseSqlDriver.RowResult(row) for row in results]
        if statement["Status"] == "FAILED":
            return None # what do we return here??

    def execute_query_raw(self, query: str) -> Optional[list[dict[str, any]]]:
        raise NotImplemented()

    def get_table_schema(self, table: str, schema: Optional[str] = None) -> Optional[str]:
        raise NotImplemented()
