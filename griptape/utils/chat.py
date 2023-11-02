from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from attr import define, field, Factory

if TYPE_CHECKING:
    from griptape.structures import Structure
from griptape.utils import Stream

@define
class Chat:
    structure: Structure = field()
    exit_keywords: list[str] = field(default=["exit"], kw_only=True)
    exiting_text: str = field(default="exiting...", kw_only=True)
    processing_text: str = field(default="processing...", kw_only=True)
    intro_text: Optional[str] = field(default=None, kw_only=True)
    prompt_prefix: str = field(default="Q: ", kw_only=True)
    response_prefix: str = field(default="A: ", kw_only=True)
    output_fn: Callable[[str], None] = field(
        default=lambda x: print (x, end=""), kw_only=True
    )
    stream: bool = field(default=False,kw_only=True)

    def start(self,initial_turn:str=None) -> None:
        if initial_turn:
            self.output_fn(initial_turn+'\n')

        self.structure.stream = self.stream
        self.structure.prompt_driver.stream = self.stream
        if self.stream:
            self.structure=Stream(self.structure)

        if self.intro_text:
            self.output_fn(self.intro_text+'\n')
        while True:
            question = input(self.prompt_prefix)

            if question.lower() in self.exit_keywords:
                self.output_fn(self.exiting_text+'\n')
                break
            else:
                self.output_fn(self.processing_text+'\n')

            if self.stream:
                self.output_fn(f"{self.response_prefix}")
                self.structure.structure.event_listeners=[] # To address https://github.com/griptape-ai/griptape/issues/408
                for chunk in self.structure.run(question):
                    self.output_fn(chunk.value)
                self.output_fn("\n")
            else:
                self.output_fn(
                    f"{self.response_prefix}{self.structure.run(question).output.to_text()}"
            )
