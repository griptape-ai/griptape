import os

from griptape.drivers.web_search.exa import ExaWebSearchDriver

driver = ExaWebSearchDriver(api_key=os.environ["EXA_API_KEY"])

driver.search("griptape ai")
