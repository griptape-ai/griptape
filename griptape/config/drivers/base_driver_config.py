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
class BaseDriverConfig(ABC, SerializableMixin):
    _prompt: BasePromptDriver = field(kw_only=True, default=None, metadata={"serializable": True}, alias="prompt")
    _image_generation: BaseImageGenerationDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="image_generation"
    )
    _image_query: BaseImageQueryDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="image_query"
    )
    _embedding: BaseEmbeddingDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="embedding"
    )
    _vector_store: BaseVectorStoreDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="vector_store"
    )
    _conversation_memory: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="conversation_memory"
    )
    _text_to_speech: BaseTextToSpeechDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="text_to_speech"
    )
    _audio_transcription: BaseAudioTranscriptionDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="audio_transcription"
    )

    @lazy_property()
    @abstractmethod
    def prompt(self) -> BasePromptDriver: ...

    @lazy_property()
    @abstractmethod
    def image_generation(self) -> BaseImageGenerationDriver: ...

    @lazy_property()
    @abstractmethod
    def image_query(self) -> BaseImageQueryDriver: ...

    @lazy_property()
    @abstractmethod
    def embedding(self) -> BaseEmbeddingDriver: ...

    @lazy_property()
    @abstractmethod
    def vector_store(self) -> BaseVectorStoreDriver: ...

    @lazy_property()
    @abstractmethod
    def conversation_memory(self) -> Optional[BaseConversationMemoryDriver]: ...

    @lazy_property()
    @abstractmethod
    def text_to_speech(self) -> BaseTextToSpeechDriver: ...

    @lazy_property()
    @abstractmethod
    def audio_transcription(self) -> BaseAudioTranscriptionDriver: ...
