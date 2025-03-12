import os

from griptape.drivers.web_search.perplexity import PerplexityWebSearchDriver

driver = PerplexityWebSearchDriver(
    api_key=os.environ["PERPLEXITY_API_KEY"],
)

print(driver.search("griptape ai").to_text())
