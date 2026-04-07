import os

from griptape.drivers.web_search.google import GoogleWebSearchDriver

driver = GoogleWebSearchDriver(
    api_key=os.environ["GOOGLE_API_KEY"],
    search_id=os.environ["GOOGLE_API_SEARCH_ID"],
)

driver.search("griptape ai")
