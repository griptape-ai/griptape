from __future__ import annotations
from abc import ABC, abstractmethod

from attr import field, define
from typing import Optional

from griptape.artifacts import MediaArtifact
from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseImageGenerationDriver, BaseAudioGenerationDriver
from griptape.rules import Ruleset


@define
class BaseAudioGenerationEngine(ABC):
    audio_generation_driver: BaseAudioGenerationDriver = field(kw_only=True)

    @abstractmethod
    def run(self, prompts: list[str], *args, **kwargs) -> AudioArtifact:
        ...
