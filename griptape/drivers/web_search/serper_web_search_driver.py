from __future__ import annotations

import json
import requests
from attrs import define, field
from enum import Enum

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseWebSearchDriver


class SerperType(str, Enum):
    SEARCH = "search"
    NEWS = "news"
    PLACES = "places"
    IMAGES = "images"
    PATENTS = "patents"


@define
class SerperWebSearchDriver(BaseWebSearchDriver):
    api_key: str = field(kw_only=True)
    type: str = field(default="search", kw_only=True)
    date_range: str = field(default=None, kw_only=True)

    def search(self, query: str, **kwargs) -> ListArtifact:
        return ListArtifact([TextArtifact(json.dumps(result)) for result in self._search_serper(query, **kwargs)])

    def _search_serper(self, query: str, **kwargs) -> list[dict]:
        # Default to search if type is not a valid SerperType
        search_type = self.type if self.type in [t.value for t in SerperType] else SerperType.SEARCH.value
        url = f"https://google.serper.dev/{search_type}"

        payload = {"q": query, **kwargs}

        if self.date_range:
            payload["tbs"] = f"qdr:{self.date_range}"

        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            data = response.json()
            results = []

            if search_type == SerperType.SEARCH.value:
                # Extracting organic results
                for r in data.get("organic", []):
                    results.append(
                        {
                            "url": r["link"],
                            "title": r["title"],
                            "description": r["snippet"],
                            "sitelinks": r.get("sitelinks", []),
                            "position": r.get("position", None),
                        }
                    )

                # Extract knowledge graph if present
                knowledge_graph = data.get("knowledgeGraph", {})
                if knowledge_graph:
                    results.append(
                        {
                            "knowledge_graph": {
                                "title": knowledge_graph.get("title"),
                                "type": knowledge_graph.get("type"),
                                "website": knowledge_graph.get("website"),
                                "imageUrl": knowledge_graph.get("imageUrl"),
                                "description": knowledge_graph.get("description"),
                                "descriptionSource": knowledge_graph.get("descriptionSource"),
                                "descriptionLink": knowledge_graph.get("descriptionLink"),
                                "attributes": knowledge_graph.get("attributes", {}),
                            }
                        }
                    )
            elif search_type == SerperType.NEWS.value:
                for r in data.get("news", []):
                    results.append(
                        {
                            "url": r["link"],
                            "title": r["title"],
                            "description": r.get("snippet"),
                            "date": r.get("date"),
                            "source": r.get("source"),
                        }
                    )
            elif search_type == SerperType.PLACES.value:
                for r in data.get("places", []):
                    results.append(
                        {
                            "position": r.get("position"),
                            "title": r.get("title"),
                            "address": r.get("address"),
                            "latitude": r.get("latitude"),
                            "longitude": r.get("longitude"),
                            "rating": r.get("rating"),
                            "ratingCount": r.get("ratingCount"),
                            "category": r.get("category"),
                            "phoneNumber": r.get("phoneNumber"),
                            "website": r.get("website"),
                            "cid": r.get("cid"),
                        }
                    )
            elif search_type == SerperType.IMAGES.value:
                for r in data.get("images", []):
                    results.append(
                        {
                            "title": r.get("title"),
                            "imageUrl": r.get("imageUrl"),
                            "imageWidth": r.get("imageWidth"),
                            "imageHeight": r.get("imageHeight"),
                            "thumbnailUrl": r.get("thumbnailUrl"),
                            "thumbnailWidth": r.get("thumbnailWidth"),
                            "thumbnailHeight": r.get("thumbnailHeight"),
                            "source": r.get("source"),
                            "domain": r.get("domain"),
                            "link": r.get("link"),
                            "googleUrl": r.get("googleUrl"),
                            "position": r.get("position"),
                        }
                    )
            elif search_type == SerperType.PATENTS.value:
                for r in data.get("organic", []):
                    results.append(
                        {
                            "title": r.get("title"),
                            "description": r.get("snippet"),
                            "url": r.get("link"),
                            "priorityDate": r.get("priorityDate"),
                            "filingDate": r.get("filingDate"),
                            "grantDate": r.get("grantDate"),
                            "publicationDate": r.get("publicationDate"),
                            "inventor": r.get("inventor"),
                            "assignee": r.get("assignee"),
                            "publicationNumber": r.get("publicationNumber"),
                            "language": r.get("language"),
                            "thumbnailUrl": r.get("thumbnailUrl"),
                            "pdfUrl": r.get("pdfUrl"),
                            "figures": r.get("figures", []),
                            "position": r.get("position"),
                        }
                    )

            return results
        else:
            raise Exception(
                f"Serper API returned an error with status code "
                f"{response.status_code} and reason '{response.reason}'",
            )
