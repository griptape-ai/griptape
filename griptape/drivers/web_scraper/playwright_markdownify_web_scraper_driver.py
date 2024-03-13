import re
from typing import Any, Optional
from attr import define, field
from griptape.drivers import BaseWebScraperDriver
from griptape.utils import import_optional_dependency


@define
class PlaywrightMarkdownifyWebScraperDriver(BaseWebScraperDriver):
    include_links: bool = field(default=True, kw_only=True)

    def scrape_url(self, url: str, *args, **kwargs) -> Optional[str]:
        playwright_sync_api = import_optional_dependency("playwright.sync_api")
        md = import_optional_dependency("markdownify").markdownify
        sync_playwright = playwright_sync_api.sync_playwright

        with sync_playwright() as p:
            with p.chromium.launch(headless=True) as browser:
                page = browser.new_page()
                page.goto(url)
                content = page.content()

                if not content:
                    raise Exception("can't access URL")

                text = md(content)

                return text
