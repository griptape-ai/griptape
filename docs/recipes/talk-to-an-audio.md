Certain models are capable of handling more modalities than text.
OpenAI's `gpt-4o-audio-preview`, for instance, can accept and produce both text as well as audio.
In this example, we'll use OpenAI's [gpt-4o-audio-preview](https://platform.openai.com/docs/guides/audio) model to re-transcribe an audio file as a pirate, and then determine the tone of the speaker.

!!! important

    `modalities=["audio", "text"]` must be provided to use this model.

!!! tip

    Try playing around with the available [voice options](https://platform.openai.com/docs/guides/text-to-speech#voice-options).

```python
--8<-- "docs/recipes/src/talk_to_an_audio_1.py"
```

!!! note

    [Text To Speech Drivers](../griptape-framework/drivers/text-to-speech-drivers.md) and [Audio Transcription Drivers](../griptape-framework/drivers/audio-transcription-drivers.md) may provide a more performant, cost-effective solution.

We can also stream back responses in real-time for a more interactive, conversational experience.
Although playing audio streams isn't a core `griptape` feature, we can implement a simple `AudioPlayer` utility with `pyaudio` to demonstrate streaming audio playback.

!!! important

    Griptape does not include `pyaudio` as a dependency. See `pyaudio`'s [installation instructions](https://pypi.org/project/PyAudio/) for details.

```python
--8<-- "docs/recipes/src/talk_to_an_audio_2.py"
```
