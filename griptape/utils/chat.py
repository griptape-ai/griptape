from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field

if TYPE_CHECKING:
    from griptape.structures import Structure


@define(frozen=True)
class Chat:
    structure: Structure = field()
    exit_keywords: list[str] = field(default=["exit"], kw_only=True)
    exiting_text: str = field(default='exiting...', kw_only=True)
    processing_text: str = field(default='processing...', kw_only=True)
    intro_text: Optional[str] = field(default=None, kw_only=True)
    prompt_prefix: str = field(default='Q: ', kw_only=True)
    response_prefix: str = field(default='A: ', kw_only=True)

    def start(self) -> None:
        if self.intro_text:
            print(self.intro_text)
        while True:
            question = input(self.prompt_prefix)

            if question.lower() in self.exit_keywords:
                print(self.exiting_text)

                break
            else:
                print(self.processing_text)

            print(f"{self.response_prefix}{self.structure.run(question).output.to_text()}")
