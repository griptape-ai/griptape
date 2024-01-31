import pytest
import boto3
from botocore.stub import Stubber
from griptape.drivers import BaseSqlDriver, AmazonRedshiftSqlDriver


class TestAmazonRedshiftSqlDriver:
    TEST_RECORDS = [
        [{"stringValue": "Bob"}, {"stringValue": "Ross"}],
        [{"stringValue": "Tony"}, {"stringValue": "Hawk"}],
    ]

    TEST_COLUMN_METADATA = [
        {
            "isCaseSensitive": True,
            "isCurrency": False,
            "isSigned": False,
            "label": "first_name",
            "length": 0,
            "name": "first_name",
            "nullable": 1,
            "precision": 256,
            "scale": 0,
            "schemaName": "public",
            "tableName": "griptape_enthusiasts",
            "typeName": "varchar",
        },
        {
            "isCaseSensitive": True,
            "isCurrency": False,
            "isSigned": False,
            "label": "last_name",
            "length": 0,
            "name": "last_name",
            "nullable": 1,
            "precision": 256,
            "scale": 0,
            "schemaName": "public",
            "tableName": "griptape_enthusiasts",
            "typeName": "varchar",
        },
    ]

    @pytest.fixture
    def statement_driver(self):
        session = boto3.Session(region_name="us-east-1")
        client = session.client("redshift-data")
        stubber = Stubber(client)
        expected_params = {"Sql": "query", "Database": "dev", "WorkgroupName": "dev"}
        response = {"Id": "responseId"}
        stubber.add_response("execute_statement", response, expected_params)

        expected_params = {"Id": "responseId"}
        response = {"Id": "responseId", "Status": "FINISHED"}
        stubber.add_response("describe_statement", response, expected_params)

        expected_params = {"Id": "responseId"}
        response = {
            "ColumnMetadata": [
                {
                    "isCaseSensitive": True,
                    "isCurrency": False,
                    "isSigned": False,
                    "label": "first_name",
                    "length": 0,
                    "name": "first_name",
                    "nullable": 1,
                    "precision": 256,
                    "scale": 0,
                    "schemaName": "public",
                    "tableName": "griptape_enthusiasts",
                    "typeName": "varchar",
                },
                {
                    "isCaseSensitive": True,
                    "isCurrency": False,
                    "isSigned": False,
                    "label": "last_name",
                    "length": 0,
                    "name": "last_name",
                    "nullable": 1,
                    "precision": 256,
                    "scale": 0,
                    "schemaName": "public",
                    "tableName": "griptape_enthusiasts",
                    "typeName": "varchar",
                },
            ],
            "Records": [
                [{"stringValue": "Bob"}, {"stringValue": "Ross"}],
                [{"stringValue": "Tony"}, {"stringValue": "Hawk"}],
            ],
            "TotalNumRows": 2,
            "ResponseMetadata": {
                "RequestId": "50033523-70b1-422b-98d7-e91045f55f8a",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "50033523-70b1-422b-98d7-e91045f55f8a",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "551",
                    "date": "Fri, 07 Jul 2023 20:38:26 GMT",
                },
                "RetryAttempts": 0,
            },
        }
        stubber.add_response("get_statement_result", response, expected_params)
        stubber.activate()

        return AmazonRedshiftSqlDriver(database="dev", session=session, workgroup_name="dev", client=client)

    @pytest.fixture
    def describe_table_driver(self):
        session = boto3.Session(region_name="us-east-1")
        client = session.client("redshift-data")
        stubber = Stubber(client)
        describe_table_response = {"ColumnList": TestAmazonRedshiftSqlDriver.TEST_COLUMN_METADATA}
        expected_params = {"Database": "dev", "WorkgroupName": "dev", "Table": "dev"}
        stubber.add_response("describe_table", describe_table_response, expected_params)

        stubber.activate()

        return AmazonRedshiftSqlDriver(database="dev", session=session, workgroup_name="dev", client=client)

    def test_amazon_redshift_sql_driver_parameter_validation_correct_params(self):
        AmazonRedshiftSqlDriver(database="dev", session=boto3.Session(region_name="us-east-1"), workgroup_name="dev")

    def test_amazon_redshift_sql_driver_parameter_validation_missing_params(self):
        with pytest.raises(ValueError):
            AmazonRedshiftSqlDriver(database="dev", session=boto3.Session(region_name="us-east-1"))

    def test_amazon_redshift_sql_driver_parameter_validation_conflicting_params(self):
        with pytest.raises(ValueError):
            AmazonRedshiftSqlDriver(
                database="dev",
                session=boto3.Session(region_name="us-east-1"),
                workgroup_name="dev",
                cluster_identifier="dev",
            )

    def test_process_rows_from_records(self):
        assert AmazonRedshiftSqlDriver._process_rows_from_records(TestAmazonRedshiftSqlDriver.TEST_RECORDS) == [
            ["Bob", "Ross"],
            ["Tony", "Hawk"],
        ]

    def test_process_columns_from_column_metadata(self):
        assert AmazonRedshiftSqlDriver._process_columns_from_column_metadata(
            TestAmazonRedshiftSqlDriver.TEST_COLUMN_METADATA
        ) == ["first_name", "last_name"]

    def test_post_process(self):
        assert AmazonRedshiftSqlDriver._post_process(
            TestAmazonRedshiftSqlDriver.TEST_COLUMN_METADATA, TestAmazonRedshiftSqlDriver.TEST_RECORDS
        ) == [{"first_name": "Bob", "last_name": "Ross"}, {"first_name": "Tony", "last_name": "Hawk"}]

    def test_execute_query_raw(self, statement_driver):
        rows = [{"first_name": "Bob", "last_name": "Ross"}, {"first_name": "Tony", "last_name": "Hawk"}]
        assert statement_driver.execute_query_raw("query") == rows

    def test_execute_query(self, statement_driver):
        rows = [{"first_name": "Bob", "last_name": "Ross"}, {"first_name": "Tony", "last_name": "Hawk"}]
        assert statement_driver.execute_query("query") == [BaseSqlDriver.RowResult(row) for row in rows]

    def test_get_table_schema(self, describe_table_driver):
        assert describe_table_driver.get_table_schema("dev") == "['first_name', 'last_name']"
