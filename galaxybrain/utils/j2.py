import os
from attrs import define, field
from jinja2 import Environment, FileSystemLoader
from galaxybrain.utils import TiktokenTokenizer, Tokenizer


@define
class J2:
    template: str = field()
    templates_path: str = field(default="prompts/templates", kw_only=True)
    tokenizer: Tokenizer = field(default=TiktokenTokenizer(), kw_only=True)
    environment: Environment = field(init=False)

    def __attrs_post_init__(self):
        import galaxybrain

        templates_dir = os.path.join(galaxybrain.PACKAGE_ABS_PATH, self.templates_path)

        self.environment = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, **kwargs):
        if not kwargs.get("stop_sequence"):
            kwargs["stop_sequence"] = self.tokenizer.stop_token

        return self.environment.get_template(self.template).render(kwargs)
