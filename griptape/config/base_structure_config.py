from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.config import BaseConfig
from griptape.events import EventListener
from griptape.mixins.event_publisher_mixin import EventPublisherMixin
from griptape.utils import dict_merge

if TYPE_CHECKING:
    from griptape.drivers import (
        BaseAudioTranscriptionDriver,
        BaseConversationMemoryDriver,
        BaseEmbeddingDriver,
        BaseImageGenerationDriver,
        BaseImageQueryDriver,
        BasePromptDriver,
        BaseTextToSpeechDriver,
        BaseVectorStoreDriver,
    )
    from griptape.structures import Structure


@define
class BaseStructureConfig(BaseConfig, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"serializable": True})
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True, metadata={"serializable": True})
    image_query_driver: BaseImageQueryDriver = field(kw_only=True, metadata={"serializable": True})
    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True, metadata={"serializable": True})
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    text_to_speech_driver: BaseTextToSpeechDriver = field(kw_only=True, metadata={"serializable": True})
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(kw_only=True, metadata={"serializable": True})

    _structure: Structure = field(default=None, kw_only=True, alias="structure")
    _event_listener: Optional[EventListener] = field(default=None, kw_only=True, alias="event_listener")

    @property
    def drivers(self) -> list:
        return [
            self.prompt_driver,
            self.image_generation_driver,
            self.image_query_driver,
            self.embedding_driver,
            self.vector_store_driver,
            self.conversation_memory_driver,
            self.text_to_speech_driver,
            self.audio_transcription_driver,
        ]

    @property
    def structure(self) -> Optional[Structure]:
        return self._structure

    @structure.setter
    def structure(self, structure: Structure) -> None:
        if structure != self.structure:
            event_publisher_drivers = [
                driver for driver in self.drivers if driver is not None and isinstance(driver, EventPublisherMixin)
            ]

            for driver in event_publisher_drivers:
                if self._event_listener is not None:
                    driver.remove_event_listener(self._event_listener)

            self._event_listener = EventListener(structure.publish_event)
            for driver in event_publisher_drivers:
                driver.add_event_listener(self._event_listener)

        self._structure = structure

    def merge_config(self, config: dict) -> BaseStructureConfig:
        base_config = self.to_dict()
        merged_config = dict_merge(base_config, config)

        return BaseStructureConfig.from_dict(merged_config)
