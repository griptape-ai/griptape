---
search:
  boost: 2 
---

## Overview
SQL drivers can be used to make SQL queries and load table schemas. They are used by the [SqlLoader](../../reference/griptape/loaders/sql_loader.md) to process data. All loaders implement the following methods:

* `execute_query()` executes a query and returns [RowResult](../../reference/griptape/drivers/sql/base_sql_driver.md#griptape.drivers.sql.base_sql_driver.BaseSqlDriver.RowResult)s.
* `execute_query_row()` executes a query and returns a raw result from SQL.
* `get_table_schema()` returns a table schema.

## SQL Drivers

### SQL

!!! info
    This driver requires the `drivers-sql` [extra](../index.md#extras).

Note that you may need to install the appropriate database driver for your SQL database.
For example, to use the `psycopg2` driver for PostgreSQL, you can install it with `pip install psycopg2-binary`.

This is a basic SQL loader based on [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/). Here is an example of how to use it:

```python
--8<-- "docs/griptape-framework/drivers/src/sql_drivers_1.py"
```

### Amazon Redshift

!!! info
    This driver requires the `drivers-sql-amazon-redshift` [extra](../index.md#extras).

This is a SQL driver for interacting with the [Amazon Redshift Data API](https://docs.aws.amazon.com/redshift-data/latest/APIReference/Welcome.html) 
to execute statements. Here is an example of how to use it for Redshift Serverless:

```python
--8<-- "docs/griptape-framework/drivers/src/sql_drivers_2.py"
```

### Snowflake

!!! info
    This driver requires the `drivers-sql-snowflake` [extra](../index.md#extras).

This is a SQL driver based on the [Snowflake SQLAlchemy Toolkit](https://docs.snowflake.com/en/developer-guide/python-connector/sqlalchemy) which runs on top of the Snowflake Connector for Python. Here is an example of how to use it:

```python
--8<-- "docs/griptape-framework/drivers/src/sql_drivers_3.py"
```
