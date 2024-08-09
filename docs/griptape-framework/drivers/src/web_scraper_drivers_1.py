import os

from griptape.drivers import ProxyWebScraperDriver

query_params = [
    "markdown_response=true",
    "js_render=false",
    "premium_proxy=false",
]
proxy_url = f'http://{os.environ["ZENROWS_API_KEY"]}:{"&".join(query_params)}@proxy.zenrows.com:8001'

driver = ProxyWebScraperDriver(
    proxies={
        "http": proxy_url,
        "https": proxy_url,
    },
    params={"verify": False},
)

driver.scrape_url("https://griptape.ai")
