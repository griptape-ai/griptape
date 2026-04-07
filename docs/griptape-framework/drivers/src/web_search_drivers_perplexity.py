import os

from griptape.drivers.web_search.perplexity import PerplexityWebSearchDriver

driver = PerplexityWebSearchDriver(
    api_key=os.environ["PERPLEXITY_API_KEY"],
)
result = driver.search("griptape ai")

print(result.to_text())
# The search results will only contain a single Artifact.
# This Artifact contains the search results and any citations.
for citation in result[0].meta["citations"]:
    print(citation)
