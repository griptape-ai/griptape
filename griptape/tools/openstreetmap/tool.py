import json  
import requests
from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal

class OpenStreetMapTool(BaseTool):
    @activity(
        config={
            "description": "Search OpenStreetMap for a location and get its details.",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="Query in the format 'location'",
                    ): str
                }
            ),
        }
    )
    def search(self, params: dict) -> TextArtifact:
        query = params["query"]
        try:
            location_details = self._search(query)
            return TextArtifact(json.dumps({"location": query}))  # Converts the dictionary to a string
        except Exception as e:
            raise Exception("An error occurred while searching for the location.") from e

    def _search(self, search_query: str) -> dict:
        overpass_ql_query = f"""
        [out:json];
        area[name="{search_query}"]->.searchArea;
        (
          node(area.searchArea);
          way(area.searchArea);
          relation(area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.get(
            "http://overpass-api.de/api/interpreter",
            params={"data": overpass_ql_query},
        )
        response.raise_for_status()
        location_details = response.json()
        return location_details
