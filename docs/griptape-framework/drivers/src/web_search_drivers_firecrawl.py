import os

from griptape.drivers.web_search.firecrawl import FirecrawlWebSearchDriver

driver = FirecrawlWebSearchDriver(api_key=os.environ["FIRECRAWL_API_KEY"])

driver.search("griptape ai")
