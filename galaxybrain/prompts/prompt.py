from attrs import define, field
from typing import Optional
from galaxybrain.rules.rule import Rule
from galaxybrain.memory import Memory
from jinja2 import Environment, FileSystemLoader
import galaxybrain
import os


@define
class Prompt():
    value: str
    rules: list[Rule] = field(default=[], kw_only=True)
    memory: Optional[Memory] = field(default=None, kw_only=True)
    j2_env: any = field(init=False)

    def __attrs_post_init__(self):
        templates_path = os.path.join(galaxybrain.PACKAGE_ABS_PATH, "prompts/templates")

        self.j2_env = Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def build(self) -> str:
        if self.memory:
            if self.memory.is_empty():
                prompt = self.intro_prompt()

                self.memory.add_memory(prompt)
            else:
                prompt = self.memory_prompt()

                self.memory.add_memory(self.format_answer(self.value))
        else:
            prompt = self.intro_prompt()

        return prompt
    
    def validate(self, value: str) -> bool:
        return all(rule.validator(value) for rule in self.rules)

    def intro_prompt(self) -> str:
        rules_text = self.j2_env.get_template("rules.j2").render(
            {
                "rules": self.rules
            }
        )

        intro_text = self.j2_env.get_template("intro.j2").render(
            {
                "question": self.format_question(self.value),
                "answer": self.format_answer("")
            },
        )

        return f"{rules_text}\n{intro_text}"
    
    def memory_prompt(self) -> str:
        return self.j2_env.get_template("memory.j2").render(
            {
                "memory": self.memory.to_string(),
                "question": self.format_question(self.value),
                "answer": self.format_answer("")
            }
        )

    def format_question(self, question: str) -> str:
        return f"Q: {question}"
    
    def format_answer(self, answer: str) -> str:
        return f"A: {answer}"