from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field

if TYPE_CHECKING:
    from griptape.structures import Structure


@define(frozen=True)
class Chat:
    structure: Structure = field()

    def start(self) -> None:
        while True:
            question = input("Q: ")

            if question.lower() == "exit":
                print("exiting...")

                break
            else:
                print("processing...")

            print(f"A: {self.structure.run(question).output.to_text()}")
