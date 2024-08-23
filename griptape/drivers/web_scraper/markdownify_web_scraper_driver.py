from __future__ import annotations

import re
from random import randint
from typing import Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver
from griptape.utils import import_optional_dependency


@define
class MarkdownifyWebScraperDriver(BaseWebScraperDriver):
    """Driver to scrape a webpage and return the content in markdown format.

    As a prerequisite to using MarkdownifyWebScraperDriver, you need to install the browsers used by
    playwright. You can do this by running: `poetry run playwright install`.
    For more details about playwright, see https://playwright.dev/python/docs/library.

    Attributes:
        include_links: If `True`, the driver will include link urls in the markdown output.
        exclude_tags: Optionally provide custom tags to exclude from the scraped content.
        exclude_classes: Optionally provide custom classes to exclude from the scraped content.
        exclude_ids: Optionally provide custom ids to exclude from the scraped content.
        timeout: Optionally provide a timeout in milliseconds for the page to continue loading after
            the browser has emitted the "load" event.
    """

    DEFAULT_EXCLUDE_TAGS = ["script", "style", "head"]

    include_links: bool = field(default=True, kw_only=True)
    exclude_tags: list[str] = field(
        default=Factory(lambda self: self.DEFAULT_EXCLUDE_TAGS, takes_self=True),
        kw_only=True,
    )
    exclude_classes: list[str] = field(default=Factory(list), kw_only=True)
    exclude_ids: list[str] = field(default=Factory(list), kw_only=True)
    timeout: Optional[int] = field(default=None, kw_only=True)

    def scrape_url(self, url: str) -> TextArtifact:
        sync_playwright = import_optional_dependency("playwright.sync_api").sync_playwright
        fake_useragent = import_optional_dependency("fake_useragent")
        bs4 = import_optional_dependency("bs4")
        markdownify = import_optional_dependency("markdownify")

        include_links = self.include_links

        # Custom MarkdownConverter to optionally linked urls. If include_links is False only
        # the text of the link is returned.
        class OptionalLinksMarkdownConverter(markdownify.MarkdownConverter):
            def convert_a(self, el: Any, text: str, convert_as_inline: Any) -> str:
                if include_links:
                    return super().convert_a(el, text, convert_as_inline)
                return text

        with sync_playwright() as p, p.chromium.launch(headless=True) as browser:
            # Randomize user agent to help prevent fingerprinting
            user_agent = fake_useragent.UserAgent().random

            # Randomize viewport size to help prevent fingerprinting
            viewport = {"width": randint(1024, 1920), "height": randint(768, 1080)}

            context = browser.new_context(user_agent=user_agent, viewport=viewport)

            # Disable WebRTC to prevent IP leaks
            context.add_init_script("""
            Object.defineProperty(navigator, 'mediaDevices', {
                value: {
                    getUserMedia: () => Promise.reject(new Error('Not allowed')),
                },
                configurable: True,
            });
            """)

            # Prevent canvas fingerprinting
            context.add_init_script("""
            HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,spoofedData";
            HTMLCanvasElement.prototype.getImageData = function(sx, sy, sw, sh) {
                const data = CanvasRenderingContext2D.prototype.getImageData.call(this, sx, sy, sw, sh);
                for (let i = 0; i < data.data.length; i += 4) data.data[i] ^= 0xFF; // Invert colors
                return data;
            };
            """)

            # Add random plugins to prevent fingerprinting
            context.add_init_script(f"""
            Object.defineProperty(navigator, 'plugins', {{
                get: () => {self._random_js_plugin_array(user_agent)},
                configurable: True,
            }});
            """)

            page = context.new_page()

            def skip_loading_images(route: Any) -> Any:
                if route.request.resource_type == "image":
                    return route.abort()
                route.continue_()
                return None

            page.route("**/*", skip_loading_images)

            page.goto(url)

            # Some websites require a delay before the content is fully loaded
            # even after the browser has emitted "load" event.
            if self.timeout:
                page.wait_for_timeout(self.timeout)

            content = page.content()

            if not content:
                raise Exception("can't access URL")

            soup = bs4.BeautifulSoup(content, "html.parser")

            # Remove unwanted elements
            exclude_selector = ",".join(
                self.exclude_tags + [f".{c}" for c in self.exclude_classes] + [f"#{i}" for i in self.exclude_ids],
            )
            if exclude_selector:
                for s in soup.select(exclude_selector):
                    s.extract()

            text = OptionalLinksMarkdownConverter().convert_soup(soup)

            # Remove leading and trailing whitespace from the entire text
            text = text.strip()

            # Remove trailing whitespace from each line
            text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

            # Indent using 2 spaces instead of tabs
            text = re.sub(r"(\n?\s*?)\t", r"\1  ", text)

            # Remove triple+ newlines (keep double newlines for paragraphs)
            text = re.sub(r"\n\n+", "\n\n", text)

            return TextArtifact(text)

    def _random_js_plugin_array(self, user_agent: str) -> str:
        faker = import_optional_dependency("faker")
        fake = faker.Faker()
        num_plugins = randint(0, 5)
        extension = self._get_os_extension(user_agent)
        plugins = []
        for _ in range(num_plugins):
            plugins.append(
                "".join(
                    [
                        "{",
                        ", ".join(
                            [
                                f'{k}: "{v}"'
                                for k, v in {
                                    "name": f"{fake.word().capitalize()} Plugin",
                                    "description": f"{fake.catch_phrase()} Description",
                                    "filename": f"{fake.file_name(extension=extension)}",
                                }.items()
                            ]
                        ),
                        "}",
                    ]
                )
            )

        return f"[{', '.join(plugins)}]"

    def _get_os_extension(self, user_agent: str) -> str:
        if "Windows" in user_agent:
            return "dll"
        elif "Macintosh" in user_agent:
            return "dylib"
        elif "Linux" in user_agent:
            return "so"
        else:
            return "plugin"  # Default fallback
