from schema import Schema, Literal, Optional as SchemaOptional
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from typing import Dict, List, Optional, Union
from duckduckgo_search import DDGS  # Make sure to install this package

class DuckDuckGoSearchAPIWrapper:
    """Wrapper for DuckDuckGo Search API."""

    region: Optional[str] = "wt-wt"
    safesearch: str = "moderate"
    timelimit: Optional[str] = "y"  # Changed from time to timelimit
    max_results: int = 5

    def get_snippets(self, query: str) -> List[str]:
        """Run query through DuckDuckGo and return concatenated results."""
        with DDGS() as ddgs:
            results = ddgs.text(
                query,
                region=self.region,
                safesearch=self.safesearch,
                timelimit=self.timelimit,  # Changed from time to timelimit
            )
            if results is None:
                return ["No good DuckDuckGo Search Result was found"]
            snippets = []
            for i, res in enumerate(results, 1):
                if res is not None:
                    snippets.append(res["body"])
                if len(snippets) == self.max_results:
                    break
        return snippets

class DDGSearch(BaseTool):
    @activity(config={
        "description": "Can be used to perform a search query on DuckDuckGo",
        "schema": Schema({
            Literal("query", description="The search query to perform"): str,
            SchemaOptional(Literal("num_results", description="Number of results to retrieve")): int  # Used SchemaOptional for clarity
        })
    })
    def search(self, params: dict) -> Union[TextArtifact, ErrorArtifact]:  # Used Union for clarity
        values = params["values"]
        num_results = values.get("num_results", 5)  # Get num_results, or use 5 as a default

        try:
            api_wrapper = DuckDuckGoSearchAPIWrapper()
            snippets = api_wrapper.get_snippets(values["query"])

            # Check for empty results
            if not snippets:
                return TextArtifact("No results found.")
            
            return TextArtifact(" ".join(snippets))

        except Exception as error:
            return ErrorArtifact(f"Error performing search: {error}")
