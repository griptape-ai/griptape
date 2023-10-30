import re
import json
import requests
from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal, Optional
from bs4 import BeautifulSoup


class YouTubeTool(BaseTool):
    @activity(config={"schema": Schema({Literal("query"): str})})
    def search(self, params: dict) -> TextArtifact:
        from youtube_transcript_api import (
            YouTubeTranscriptApi,
        )  # Import youtube_transcript_api at the method level
        from bs4 import BeautifulSoup  # Import bs4 at the method level

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
        from bs4 import BeautifulSoup  # Import bs4 at the method level

        search_url = (
            f"https://www.youtube.com/results?search_query={search_query}"
        )
        page = requests.get(search_url)
        soup = BeautifulSoup(page.content, "html.parser")
        video_links = soup.find_all("a", {"class": "yt-uix-tile-link"})
        video_urls = [
            "https://www.youtube.com" + link["href"] for link in video_links
        ]
        return video_urls

    def _get_transcriptions(
        self, video_ids: list[str]
    ) -> dict[str, list[dict]]:
        from youtube_transcript_api import (
            YouTubeTranscriptApi,
        )  # Import youtube_transcript_api at the method level

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
