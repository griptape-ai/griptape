import re
import json
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi
from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal, Optional


class YouTubeTool(BaseTool):  # Renamed the class to YouTubeTool
    @activity(
        config={
            "description": "Search YouTube videos based on a search query and get their transcriptions.",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="Query in the format 'search_query, num_results'",
                    ): str
                }
            ),
        }
    )
    def search(self, params: dict) -> TextArtifact:
        query = params["query"]
        search_query, num_results = self.parse_query(query)
        video_urls = self._search(search_query, num_results)
        transcriptions = self._get_transcriptions(video_urls)
        return TextArtifact(transcriptions)

    def parse_query(self, query: str) -> tuple[str, int]:
        match = re.match(
            r"(?P<search_query>.+),\s*(?P<num_results>\d+)?", query
        )
        if not match:
            raise ValueError("Invalid query format")

        search_query = match.group("search_query")
        num_results = (
            int(match.group("num_results")) if match.group("num_results") else 2
        )

        return search_query, num_results

    def _search(self, search_query: str, num_results: int) -> list[str]:
        results = YoutubeSearch(search_query, max_results=num_results).to_json()
        data = json.loads(results)
        url_suffix_list = [
            video["url_suffix"].split("=")[-1] for video in data["videos"]
        ]
        return url_suffix_list

    def _get_transcriptions(
        self, video_ids: list[str]
    ) -> dict[str, list[dict]]:
        transcriptions = {}
        for video_id in video_ids:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcriptions[video_id] = transcript_list
            except Exception as e:
                print(
                    f"An error occurred while fetching the transcript for {video_id}: {str(e)}"
                )
                continue
        return transcriptions
