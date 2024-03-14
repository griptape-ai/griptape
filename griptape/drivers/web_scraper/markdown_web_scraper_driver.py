from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseWebScraperDriver
from griptape.utils import import_optional_dependency


@define
class MarkdownWebScraperDriver(BaseWebScraperDriver):
    include_links: bool = field(default=True, kw_only=True)
    exclude_tags: list[str] = field(default=Factory(lambda: ["script","style","head","header","footer"]), kw_only=True)
    exclude_classes: list[str] = field(default=Factory(list), kw_only=True)
    exclude_ids: list[str] = field(default=Factory(list), kw_only=True)

    def scrape_url(self, url: str, *args, **kwargs) -> Optional[str]:
        sync_playwright = import_optional_dependency("playwright.sync_api").sync_playwright
        BeautifulSoup = import_optional_dependency("bs4").BeautifulSoup
        MarkdownConverter = import_optional_dependency("markdownify").MarkdownConverter
        
        include_links = self.include_links

        # Custom MarkdownConverter to optionally linked urls. If include_links is False only
        # the text of the link is returned.
        class OptionalLinksMarkdownConverter(MarkdownConverter):
            def convert_a(self, el, text, convert_as_inline):
                if include_links:
                    return super().convert_a(el, text, convert_as_inline)
                return text

        def md(html, **options):
            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted elements
            exclude_selector = ",".join(
                self.exclude_tags
                + [f".{c}" for c in self.exclude_classes]
                + [f"#{i}" for i in self.exclude_ids]
            )
            for s in soup.select(exclude_selector):
                s.extract()

            return OptionalLinksMarkdownConverter(**options).convert_soup(soup)

        with sync_playwright() as p:
            with p.chromium.launch(headless=True) as browser:
                page = browser.new_page()
                page.goto(url)
                content = page.content()

                if not content:
                    raise Exception("can't access URL")

                text = md(content)

                return text

