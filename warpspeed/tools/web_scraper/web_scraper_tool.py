import json
from typing import Union
import trafilatura
from attrs import define, field
from llama_index import GPTSimpleVectorIndex, Document
from trafilatura.settings import use_config
from warpspeed.tools import Tool


@define
class WebScraperTool(Tool):
    include_links: bool = field(default=True, kw_only=True)

    def run(self, args: dict[str]) -> str:
        url = args.get("url")
        action = args.get("action")

        try:
            return self.execute_action(url, action, args)
        except Exception as e:
            return f"error scraping page: {e}"

    def execute_action(self, url: str, action: str, args: dict[str]) -> Union[str, list[str]]:
        config = use_config()
        page = trafilatura.fetch_url(url)

        # This disables signal, so that this tool can work any thread:
        # https://trafilatura.readthedocs.io/en/latest/usage-python.html#disabling-signal
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

        if page is None:
            return "error: can't access URL"
        else:
            text = json.loads(
                trafilatura.extract(
                    page,
                    include_links=self.include_links,
                    output_format="json",
                    config=config
                )
            )

            index = GPTSimpleVectorIndex([
                Document(text.get("text"))
            ])

            if action == "get_title":
                return text.get("title")
            elif action == "get_full_text":
                return text.get("text")
            elif action == "get_author":
                return text.get("author")
            elif action == "search":
                return str(index.query(args.get("query"))).strip()
            elif action == "summarize":
                return str(index.query("Give me a short summary of this text")).strip()
            elif action == "get_keywords":
                return str(index.query("Give me a list of keywords describing this text")).strip()
            else:
                return "invalid action name"
