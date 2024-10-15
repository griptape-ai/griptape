from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field
from rich import print as rprint
from rich.prompt import Prompt

from griptape.utils.stream import Stream

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class Chat:
    class ChatPrompt(Prompt):
        prompt_suffix = ""  # We don't want rich's default prompt suffix

    structure: Structure = field()
    exit_keywords: list[str] = field(default=["exit"], kw_only=True)
    exiting_text: str = field(default="Exiting...", kw_only=True)
    processing_text: str = field(default="Thinking...", kw_only=True)
    intro_text: Optional[str] = field(default=None, kw_only=True)
    prompt_prefix: str = field(default="User: ", kw_only=True)
    response_prefix: str = field(default="Assistant: ", kw_only=True)
    input_fn: Callable[[str], str] = field(
        default=Factory(lambda self: self.default_input_fn, takes_self=True), kw_only=True
    )
    output_fn: Callable[..., None] = field(
        default=Factory(lambda self: self.default_output_fn, takes_self=True),
        kw_only=True,
    )
    logger_level: int = field(default=logging.ERROR, kw_only=True)

    def default_input_fn(self, prompt_prefix: str) -> str:
        return Chat.ChatPrompt.ask(prompt_prefix)

    def default_output_fn(self, text: str, *, stream: bool = False) -> None:
        if stream:
            rprint(text, end="", flush=True)
        else:
            rprint(text)

    def start(self) -> None:
        from griptape.configs import Defaults

        # Hide Griptape's logging output except for errors
        old_logger_level = logging.getLogger(Defaults.logging_config.logger_name).getEffectiveLevel()
        logging.getLogger(Defaults.logging_config.logger_name).setLevel(self.logger_level)

        if self.intro_text:
            self.output_fn(self.intro_text)

        has_streaming_tasks = self._has_streaming_tasks()
        while True:
            question = self.input_fn(self.prompt_prefix)

            if question.lower() in self.exit_keywords:
                self.output_fn(self.exiting_text)
                break

            if has_streaming_tasks:
                self.output_fn(self.processing_text)
                stream = Stream(self.structure).run(question)
                first_chunk = next(stream)
                self.output_fn(self.response_prefix + first_chunk.value, stream=True)
                for chunk in stream:
                    self.output_fn(chunk.value, stream=True)
            else:
                self.output_fn(self.processing_text)
                self.output_fn(f"{self.response_prefix}{self.structure.run(question).output_task.output.to_text()}")

        # Restore the original logger level
        logging.getLogger(Defaults.logging_config.logger_name).setLevel(old_logger_level)

    def _has_streaming_tasks(self) -> bool:
        from griptape.tasks.prompt_task import PromptTask

        return any(isinstance(task, PromptTask) and task.prompt_driver.stream for task in self.structure.tasks)
