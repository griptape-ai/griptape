from __future__ import annotations

import inspect
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
    """Utility for running a chat with a Structure.

    Attributes:
        structure: The Structure to run.
        exit_keywords: Keywords that will exit the chat.
        exiting_text: Text to display when exiting the chat.
        processing_text: Text to display while processing the user's input.
        intro_text: Text to display when the chat starts.
        prompt_prefix: Prefix for the user's input.
        response_prefix: Prefix for the assistant's response.
        handle_input: Function to get the user's input.
        handle_output: Function to output text. Takes a `text` argument for the text to output.
                   Also takes a `stream` argument which will be set to True when streaming Prompt Tasks are present.
    """

    class ChatPrompt(Prompt):
        prompt_suffix = ""  # We don't want rich's default prompt suffix

    structure: Structure = field()
    exit_keywords: list[str] = field(default=["exit"], kw_only=True)
    exiting_text: str = field(default="Exiting...", kw_only=True)
    processing_text: str = field(default="Thinking...", kw_only=True)
    intro_text: Optional[str] = field(default=None, kw_only=True)
    prompt_prefix: str = field(default="User: ", kw_only=True)
    response_prefix: str = field(default="Assistant: ", kw_only=True)
    handle_input: Callable[[str], str] = field(
        default=Factory(lambda self: self.default_handle_input, takes_self=True), kw_only=True
    )
    handle_output: Callable[..., None] = field(
        default=Factory(lambda self: self.default_handle_output, takes_self=True),
        kw_only=True,
    )
    logger_level: int = field(default=logging.ERROR, kw_only=True)

    def default_handle_input(self, prompt_prefix: str) -> str:
        return Chat.ChatPrompt.ask(prompt_prefix)

    def default_handle_output(self, text: str, *, stream: bool = False) -> None:
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
            self._call_handle_output(self.intro_text)

        has_streaming_tasks = self._has_streaming_tasks()
        while True:
            question = self.handle_input(self.prompt_prefix)

            if question.lower() in self.exit_keywords:
                self._call_handle_output(self.exiting_text)
                break

            if has_streaming_tasks:
                self._call_handle_output(self.processing_text)
                stream = Stream(self.structure).run(question)
                first_chunk = next(stream)
                self._call_handle_output(self.response_prefix + first_chunk.value, stream=True)
                for chunk in stream:
                    self._call_handle_output(chunk.value, stream=True)
            else:
                self._call_handle_output(self.processing_text)
                self._call_handle_output(
                    f"{self.response_prefix}{self.structure.run(question).output_task.output.to_text()}"
                )

        # Restore the original logger level
        logging.getLogger(Defaults.logging_config.logger_name).setLevel(old_logger_level)

    def _has_streaming_tasks(self) -> bool:
        from griptape.tasks.prompt_task import PromptTask

        return any(isinstance(task, PromptTask) and task.prompt_driver.stream for task in self.structure.tasks)

    def _call_handle_output(self, text: str, *, stream: bool = False) -> None:
        func_params = inspect.signature(self.handle_output).parameters.copy()
        has_kwargs = False
        for param in func_params.values():
            # if there is a **kwargs parameter, we can safely
            # pass all the params to the function
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                has_kwargs = True
                break

        if "stream" in func_params or has_kwargs:
            self.handle_output(text, stream=stream)
        else:
            self.handle_output(text)
