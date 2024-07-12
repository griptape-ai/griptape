from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field

from griptape.utils.stream import Stream

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class Chat:
    structure: Structure = field()
    exit_keywords: list[str] = field(default=["exit"], kw_only=True)
    exiting_text: str = field(default="Exiting...", kw_only=True)
    processing_text: str = field(default="Thinking...", kw_only=True)
    intro_text: Optional[str] = field(default=None, kw_only=True)
    prompt_prefix: str = field(default="User: ", kw_only=True)
    response_prefix: str = field(default="Assistant: ", kw_only=True)
    output_fn: Callable[[str], None] = field(
        default=Factory(lambda self: self.default_output_fn, takes_self=True),
        kw_only=True,
    )

    def default_output_fn(self, text: str) -> None:
        if self.structure.config.prompt_driver.stream:
            print(text, end="", flush=True)  # noqa: T201
        else:
            print(text)  # noqa: T201

    def start(self) -> None:
        if self.intro_text:
            self.output_fn(self.intro_text)
        while True:
            question = input(self.prompt_prefix)

            if question.lower() in self.exit_keywords:
                self.output_fn(self.exiting_text)
                break

            if self.structure.config.prompt_driver.stream:
                self.output_fn(self.processing_text + "\n")
                stream = Stream(self.structure).run(question)
                first_chunk = next(stream)
                self.output_fn(self.response_prefix + first_chunk.value)
                for chunk in stream:
                    self.output_fn(chunk.value)
            else:
                self.output_fn(self.processing_text)
                self.output_fn(f"{self.response_prefix}{self.structure.run(question).output_task.output.to_text()}")
