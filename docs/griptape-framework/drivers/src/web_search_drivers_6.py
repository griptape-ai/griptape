import os

from griptape.drivers import ExaWebSearchDriver

driver = ExaWebSearchDriver(api_key=os.environ["EXA_API_KEY"])

driver.search("griptape ai")
