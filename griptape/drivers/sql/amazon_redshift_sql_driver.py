import time
from typing import Optional
import boto3
from griptape.drivers import BaseSqlDriver
from attr import define, field


@define
class AmazonRedshiftSqlDriver(BaseSqlDriver):
    database: str = field(kw_only=True)
    cluster_identifier: str = field(default=None, kw_only=True)
    workgroup_name: str = field(default=None, kw_only=True)
    db_user: str = field(default=None, kw_only=True)
    secret_arn: str = field(default=None, kw_only=True)
    region_name: str = field(default="us-east-1", kw_only=True)
    wait_sec: float = field(default=0.3, kw_only=True)
    client = field(default=None, kw_only=True)

    def __attrs_post_init__(self):
        if self.client == None:
            session = boto3.Session(region_name=self.region_name)
            self.client = session.client("redshift-data")

    @staticmethod
    def _process_rows_from_records(records) -> list[list]:
        rows = []
        for r in records:
            tmp = [c[list(c.keys())[0]] for c in r]
            rows.append(tmp)
        return rows

    @staticmethod
    def _process_cells_from_rows_and_columns(
        columns: list, rows: list[list]
    ) -> list[dict[str, any]]:
        return [{column: r[idx] for idx, column in enumerate(columns)} for r in rows]

    @staticmethod
    def _process_columns_from_column_metadata(meta) -> list:
        return [k["name"] for k in meta]

    @staticmethod
    def _post_process(meta, records) -> list[dict[str, any]]:
        columns = AmazonRedshiftSqlDriver._process_columns_from_column_metadata(meta)
        rows = AmazonRedshiftSqlDriver._process_rows_from_records(records)
        return AmazonRedshiftSqlDriver._process_cells_from_rows_and_columns(
            columns, rows
        )

    def execute_query(self, query: str) -> Optional[list[BaseSqlDriver.RowResult]]:
        rows = self.execute_query_raw(query)
        return [BaseSqlDriver.RowResult(row) for row in rows]

    def execute_query_raw(self, query: str) -> Optional[list[dict[str, any]]]:
        function_kwargs = {"Sql": query, "Database": self.database}
        if self.workgroup_name:
            function_kwargs["WorkgroupName"] = self.workgroup_name
        if self.cluster_identifier:
            function_kwargs["ClusterIdentifier"] = self.cluster_identifier
        if self.db_user:
            function_kwargs["DbUser"] = self.db_user
        if self.secret_arn:
            function_kwargs["SecretArn"] = self.secret_arn

        response = self.client.execute_statement(**function_kwargs)
        response_id = response["Id"]

        statement = self.client.describe_statement(Id=response_id)

        while statement["Status"] in ["SUBMITTED", "PICKED", "STARTED"]:
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

            return AmazonRedshiftSqlDriver._post_process(
                statement_result["ColumnMetadata"], results
            )

        if statement["Status"] in ["FAILED", "ABORTED"]:
            return None

    def get_table_schema(
        self, table: str, schema: Optional[str] = None
    ) -> Optional[str]:
        function_kwargs = {"Database": self.database, "Table": table}
        if schema:
            function_kwargs["Schema"] = schema
        if self.workgroup_name:
            function_kwargs["WorkgroupName"] = self.workgroup_name
        if self.cluster_identifier:
            function_kwargs["ClusterIdentifier"] = self.cluster_identifier
        if self.db_user:
            function_kwargs["DbUser"] = self.db_user
        if self.secret_arn:
            function_kwargs["SecretArn"] = self.secret_arn
        response = self.client.describe_table(**function_kwargs)
        return [col["name"] for col in response["ColumnList"]]
