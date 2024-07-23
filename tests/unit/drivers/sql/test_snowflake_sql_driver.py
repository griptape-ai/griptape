from dataclasses import dataclass
from typing import Any
from unittest import mock

import pytest
from snowflake.connector import SnowflakeConnection
from sqlalchemy import create_engine

from griptape.drivers import BaseSqlDriver, SnowflakeSqlDriver


class TestSnowflakeSqlDriver:
    TEST_ROWS = [{"first_name": "Tony", "last_name": "Hawk"}, {"first_name": "Bob", "last_name": "Ross"}]

    TEST_COLUMNS = [("first_name", "VARCHAR"), ("last_name", "VARCHAR")]

    @pytest.fixture()
    def mock_table(self, mocker):
        @dataclass
        class Column:
            name: str
            type: str = "VARCHAR"

        mock_table = mocker.MagicMock(name="table", columns=[Column("first_name"), Column("last_name")])
        return mock_table

    @pytest.fixture()
    def mock_metadata(self, mocker):
        mock_meta = mocker.MagicMock(name="metadata")
        mock_meta.reflect.return_value = None
        return mock_meta

    @pytest.fixture()
    def mock_snowflake_engine(self, mocker):
        mock_engine = mocker.MagicMock(name="engine")
        result_mock = mocker.MagicMock(name="result")
        items_mock = mocker.MagicMock(name="items")
        items_mock_2 = mocker.MagicMock(name="items2")

        items_mock._mapping = [("first_name", "Tony"), ("last_name", "Hawk")]
        items_mock_2._mapping = [("first_name", "Bob"), ("last_name", "Ross")]

        result_mock.return_value.returns_rows = True
        result_mock.__iter__.return_value = iter([items_mock, items_mock_2])

        mock_engine.connect.return_value.__enter__.return_value.execute.return_value = result_mock

        return mock_engine

    @pytest.fixture()
    def mock_snowflake_connection(self, mocker):
        mock_connection = mocker.MagicMock(spec=SnowflakeConnection, name="connection")
        return mock_connection

    @pytest.fixture()
    def mock_snowflake_connection_no_schema(self, mocker):
        mock_connection = mocker.MagicMock(spec=SnowflakeConnection, name="connection_no_schema", schema=None)
        return mock_connection

    @pytest.fixture()
    def mock_snowflake_connection_no_database(self, mocker):
        mock_connection = mocker.MagicMock(spec=SnowflakeConnection, name="connection_no_database", database=None)
        return mock_connection

    @pytest.fixture()
    def driver(self, mock_snowflake_engine, mock_snowflake_connection):
        def get_connection():
            return mock_snowflake_connection

        new_driver = SnowflakeSqlDriver(connection_func=get_connection, engine=mock_snowflake_engine)

        return new_driver

    def test_connection_function_wrong_return_type(self):
        def get_connection() -> Any:
            return object

        with pytest.raises(ValueError):
            SnowflakeSqlDriver(connection_func=get_connection)

    def test_connection_validation_no_schema(self, mock_snowflake_connection_no_schema):
        def get_connection():
            return mock_snowflake_connection_no_schema

        with pytest.raises(ValueError):
            SnowflakeSqlDriver(connection_func=get_connection)

    def test_connection_validation_no_database(self, mock_snowflake_connection_no_database):
        def get_connection():
            return mock_snowflake_connection_no_database

        with pytest.raises(ValueError):
            SnowflakeSqlDriver(connection_func=get_connection)

    def test_engine_url_validation_wrong_engine(self, mock_snowflake_connection):
        with pytest.raises(ValueError):
            SnowflakeSqlDriver(connection_func=mock_snowflake_connection, engine=create_engine("sqlite:///:memory:"))

    def test_execute_query(self, driver):
        assert driver.execute_query("query") == [
            BaseSqlDriver.RowResult(row) for row in TestSnowflakeSqlDriver.TEST_ROWS
        ]

    def test_execute_query_raw(self, driver):
        assert driver.execute_query_raw("query") == TestSnowflakeSqlDriver.TEST_ROWS

    def test_table(self, driver, mock_table, mock_metadata):
        with mock.patch("sqlalchemy.Table", return_value=mock_table), mock.patch(
            "sqlalchemy.MetaData", return_value=mock_metadata
        ):
            assert driver.get_table_schema("table") == str(TestSnowflakeSqlDriver.TEST_COLUMNS)
