from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.mixins import SerializableMixin
from griptape.utils.decorators import lazy_property

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


@define
class BaseDriversConfig(ABC, SerializableMixin):
    _prompt_driver: BasePromptDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="prompt_driver"
    )
    _image_generation_driver: BaseImageGenerationDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="image_generation_driver"
    )
    _image_query_driver: BaseImageQueryDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="image_query_driver"
    )
    _embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="embedding_driver"
    )
    _vector_store_driver: BaseVectorStoreDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="vector_store_driver"
    )
    _conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="conversation_memory_driver"
    )
    _text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="text_to_speech_driver"
    )
    _audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="audio_transcription_driver"
    )

    @lazy_property()
    @abstractmethod
    def prompt_driver(self) -> BasePromptDriver: ...

    @lazy_property()
    @abstractmethod
    def image_generation_driver(self) -> BaseImageGenerationDriver: ...

    @lazy_property()
    @abstractmethod
    def image_query_driver(self) -> BaseImageQueryDriver: ...

    @lazy_property()
    @abstractmethod
    def embedding_driver(self) -> BaseEmbeddingDriver: ...

    @lazy_property()
    @abstractmethod
    def vector_store_driver(self) -> BaseVectorStoreDriver: ...

    @lazy_property()
    @abstractmethod
    def conversation_memory_driver(self) -> Optional[BaseConversationMemoryDriver]: ...

    @lazy_property()
    @abstractmethod
    def text_to_speech_driver(self) -> BaseTextToSpeechDriver: ...

    @lazy_property()
    @abstractmethod
    def audio_transcription_driver(self) -> BaseAudioTranscriptionDriver: ...
