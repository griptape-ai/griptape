from griptape.drivers import SqlDriver

driver = SqlDriver(engine_url="sqlite:///:memory:")

driver.execute_query("select 'foo', 'bar';")
