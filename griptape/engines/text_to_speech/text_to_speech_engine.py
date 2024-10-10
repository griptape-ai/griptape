from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.configs import Defaults

if TYPE_CHECKING:
    from griptape.artifacts.audio_artifact import AudioArtifact
    from griptape.drivers import BaseTextToSpeechDriver


@define
class TextToSpeechEngine:
    text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=Factory(lambda: Defaults.drivers_config.text_to_speech_driver), kw_only=True
    )
    prompt_joiner: str = field(default=". ", kw_only=True)

    def run(self, prompts: list[str], *args, **kwargs) -> list[AudioArtifact]:
        prompt_str = self.prompt_joiner.join(prompts).strip()
        new_prompts = [
            prompt_str[i : i + self.text_to_speech_driver.max_characters]
            for i in range(0, len(prompt_str), self.text_to_speech_driver.max_characters)
        ]
        return [self.text_to_speech_driver.try_text_to_audio(prompt=prompt) for prompt in new_prompts]
