## Overview

Web Scraper Drivers can be used to scrape text from the web. They are used by [WebLoader](../../reference/griptape/loaders/web_loader.md) to provide its functionality. All Web Scraper Drivers implement the following methods:

* `scrape_url()` scrapes text from a website and returns a [TextArtifact](../../reference/griptape/artifacts/text_artifact.md). The format of the scrapped text is determined by the Driver.

## Markdownify Web Scraper Driver

!!! info
    This driver requires the `drivers-web-scraper-markdownify` [extra](../index.md#extras) and the
    playwright browsers to be installed.

    To install the playwright browsers, run `playwright install` in your terminal. If you are using
    poetry, run `poetry run playwright install` instead. The `playwright` command should already be
    installed as a dependency of the `drivers-web-scraper-markdownify` extra. For more details about
    playwright, see [the playwright docs](https://playwright.dev/python/docs/library).

    Note that if you skip installing the playwright browsers, you will see the following error when
    you run your code:

    ```
    playwright._impl._errors.Error: Executable doesn't exist at ...
    ╔════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright was just installed or updated.       ║
    ║ Please run the following command to download new browsers: ║
    ║                                                            ║
    ║     playwright install                                     ║
    ║                                                            ║
    ║ <3 Playwright Team                                         ║
    ╚════════════════════════════════════════════════════════════╝
    ```

The [MarkdownifyWebScraperDriver](../../reference/griptape/drivers/web_scraper/markdownify_web_scraper_driver.md) outputs the scraped text in markdown format. It uses [playwright](https://pypi.org/project/playwright/) to render web pages along with dynamically loaded content, and a combination of [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) and [markdownify](https://pypi.org/project/markdownify/) to produce a markdown representation of a webpage. It makes a best effort to produce a markdown representation of a webpage that is concise yet human (and LLM) readable.

Example using `MarkdownifyWebScraperDriver` directly:

```python
from griptape.drivers import MarkdownifyWebScraperDriver

driver = MarkdownifyWebScraperDriver()

driver.scrape_url("https://griptape.ai")
```

Example of using `MarkdownifyWebScraperDriver` with an agent:

```python
from griptape.drivers import MarkdownifyWebScraperDriver
from griptape.loaders import WebLoader
from griptape.tools import TaskMemoryClient, WebScraper
from griptape.structures import Agent

agent = Agent(
    tools=[
        WebScraper(
            web_loader=WebLoader(
                web_scraper_driver=MarkdownifyWebScraperDriver(timeout=1000)
            ),
            off_prompt=True,
        ),
        TaskMemoryClient(off_prompt=False),
    ],
)
agent.run("List all email addresses on griptape.ai in a flat numbered markdown list.")
```

## Trafilatura Web Scraper Driver

!!! info
    This driver requires the `drivers-web-scraper-trafilatura` [extra](../index.md#extras).

The [TrafilaturaWebScraperDriver](../../reference/griptape/drivers/web_scraper/trafilatura_web_scraper_driver.md) scrapes text from a webpage using the [Trafilatura](https://trafilatura.readthedocs.io) library.

Example of using `TrafilaturaWebScraperDriver` directly:

```python
from griptape.drivers import TrafilaturaWebScraperDriver

driver = TrafilaturaWebScraperDriver()

driver.scrape_url("https://griptape.ai")
```
