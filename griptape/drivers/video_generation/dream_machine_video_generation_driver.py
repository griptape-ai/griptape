from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import requests
from attrs import Factory, define, field

from griptape.artifacts import VideoArtifact
from griptape.drivers import BaseVideoGenerationDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from lumaai import LumaAI

logger = logging.getLogger(__name__)


@define
class DreamMachineVideoGenerationDriver(BaseVideoGenerationDriver):
    api_key: str = field(kw_only=True, metadata={"serializable": True})
    client: LumaAI = field(
        default=Factory(
            lambda self: import_optional_dependency("lumaai").LumaAI(auth_token=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    params: dict[str, Any] = field(default={}, kw_only=True, metadata={"serializable": True})

    def try_text_to_video(self, prompt: str) -> VideoArtifact:
        response = self.client.generations.create(prompt=prompt, **self.params)
        generation = response
        status = generation.state
        while status in ["dreaming", "queued"]:
            time.sleep(5)
            if not generation.id:
                raise Exception("Generation ID not found in the response")

            generation = self.client.generations.get(generation.id)
            status = generation.state
        if status == "completed":
            video_url = generation.assets.video
            if not video_url:
                raise Exception("Video URL not found in the generation response")
            video_binary = self._download_video(video_url)
            return VideoArtifact(
                value=video_binary,
            )
        else:
            raise Exception(f"Video generation failed with status: {status}")

    def _download_video(self, video_url: str) -> bytes:
        response = requests.get(video_url)
        response.raise_for_status()
        return response.content
