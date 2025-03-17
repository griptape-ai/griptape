from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Optional

import attrs
import pyaudio  # pyright: ignore[reportMissingModuleSource]

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.events.audio_chunk_event import AudioChunkEvent
from griptape.structures.agent import Agent

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


@attrs.define
class AudioPlayer:
    """Simple audio player using PyAudio."""

    format: int = attrs.field(default=pyaudio.paInt16)
    channels: int = attrs.field(default=1)
    rate: int = attrs.field(default=24000)
    chunk_size: int = attrs.field(default=1024)

    audio: pyaudio.PyAudio = attrs.field(default=attrs.Factory(lambda: pyaudio.PyAudio()))
    stream: pyaudio.Stream = attrs.field(init=False)

    def __enter__(self) -> Self:
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size,
        )
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def write(self, audio_bytes: bytes) -> None:
        """Write audio bytes to the audio player. i.e. play the audio."""
        for i in range(0, len(audio_bytes), self.chunk_size):
            chunk = audio_bytes[i : i + self.chunk_size]
            self.stream.write(chunk)

    def close(self) -> None:
        """Close the audio player and terminate resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()


agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(
        model="gpt-4o-audio-preview",
        modalities=["audio", "text"],
        audio={"voice": "sage", "format": "pcm16"},
        stream=True,
    )
)


with AudioPlayer() as audio_player:
    for event in agent.run_stream("Hi there"):
        if isinstance(event, AudioChunkEvent):
            audio_player.write(base64.b64decode(event.data))
