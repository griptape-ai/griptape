from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from griptape.drivers import (
        BaseAudioTranscriptionDriver,
        BaseConversationMemoryDriver,
        BaseEmbeddingDriver,
        BaseImageGenerationDriver,
        BasePromptDriver,
        BaseRulesetDriver,
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
    _embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=None, metadata={"serializable": True}, alias="embedding_driver"
    )
    _vector_store_driver: BaseVectorStoreDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="vector_store_driver"
    )
    _conversation_memory_driver: BaseConversationMemoryDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="conversation_memory_driver"
    )
    _text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="text_to_speech_driver"
    )
    _audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="audio_transcription_driver"
    )
    _ruleset_driver: BaseRulesetDriver = field(
        default=None, kw_only=True, metadata={"serializable": True}, alias="ruleset_driver"
    )

    _last_drivers_config: Optional[BaseDriversConfig] = field(default=None)

    def __enter__(self) -> BaseDriversConfig:
        from griptape.configs import Defaults

        self._last_drivers_config = Defaults.drivers_config

        Defaults.drivers_config = self

        return self

    def __exit__(self, type, value, traceback) -> None:  # noqa: ANN001, A002
        from griptape.configs import Defaults

        if self._last_drivers_config is not None:
            Defaults.drivers_config = self._last_drivers_config

        self._last_drivers_config = None

    @lazy_property()
    @abstractmethod
    def prompt_driver(self) -> BasePromptDriver: ...

    @lazy_property()
    @abstractmethod
    def image_generation_driver(self) -> BaseImageGenerationDriver: ...

    @lazy_property()
    @abstractmethod
    def embedding_driver(self) -> BaseEmbeddingDriver: ...

    @lazy_property()
    @abstractmethod
    def vector_store_driver(self) -> BaseVectorStoreDriver: ...

    @lazy_property()
    @abstractmethod
    def conversation_memory_driver(self) -> BaseConversationMemoryDriver: ...

    @lazy_property()
    @abstractmethod
    def text_to_speech_driver(self) -> BaseTextToSpeechDriver: ...

    @lazy_property()
    @abstractmethod
    def audio_transcription_driver(self) -> BaseAudioTranscriptionDriver: ...

    @lazy_property()
    @abstractmethod
    def ruleset_driver(self) -> BaseRulesetDriver: ...
