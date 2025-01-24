from griptape.drivers.sql.sql_driver import SqlDriver

driver = SqlDriver(engine_url="sqlite:///:memory:")

driver.execute_query("select 'foo', 'bar';")
