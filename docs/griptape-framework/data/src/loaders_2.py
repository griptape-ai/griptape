from griptape.drivers import SqlDriver
from griptape.loaders import SqlLoader

SqlLoader(sql_driver=SqlDriver(engine_url="sqlite:///:memory:")).load("SELECT 'foo', 'bar'")

SqlLoader(sql_driver=SqlDriver(engine_url="sqlite:///:memory:")).load_collection(
    ["SELECT 'foo', 'bar';", "SELECT 'fizz', 'buzz';"]
)
