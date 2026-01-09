from __future__ import annotations

import io
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.drivers.audio_transcription import BaseAudioTranscriptionDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import openai


@define
class OpenAiAudioTranscriptionDriver(BaseAudioTranscriptionDriver):
    # These defaults were changed from openai.api_type, openai.api_version, and openai.organization
    # to None because those module-level attributes don't exist in OpenAI SDK v1.0+
    api_type: Optional[str] = field(default=None, kw_only=True)
    api_version: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    _client: Optional["openai.OpenAI"] = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )

    @lazy_property()
    def client(self) -> "openai.OpenAI":
        openai = import_optional_dependency("openai")
        return openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization)

    def try_run(self, audio: AudioArtifact, prompts: Optional[list[str]] = None) -> TextArtifact:
        additional_params = {}

        if prompts is not None:
            additional_params["prompt"] = ", ".join(prompts)

        transcription = self.client.audio.transcriptions.create(
            # Even though we're not actually providing a file to the client, the API still requires that we send a file
            # name. We set the file name to use the same format as the audio file so that the API can reject
            # it if the format is unsupported.
            model=self.model,
            file=(f"a.{audio.format}", io.BytesIO(audio.value)),
            response_format="json",
            **additional_params,
        )

        return TextArtifact(value=transcription.text)
