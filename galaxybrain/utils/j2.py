import os
from typing import Optional

from attrs import define, field
from jinja2 import Environment, FileSystemLoader
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
import galaxybrain


@define
class J2:
    template_name: Optional[str] = field(default=None)
    templates_dir: str = field(default=os.path.join(galaxybrain.PACKAGE_ABS_PATH, "templates"), kw_only=True)
    tokenizer: Tokenizer = field(default=TiktokenTokenizer(), kw_only=True)
    environment: Environment = field(init=False)

    def __attrs_post_init__(self):
        self.environment = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, **kwargs):
        if not kwargs.get("stop_sequence"):
            kwargs["stop_sequence"] = self.tokenizer.stop_token

        return self.environment.get_template(self.template_name).render(kwargs)

    def render_from_string(self, value: str, **kwargs):
        if not kwargs.get("stop_sequence"):
            kwargs["stop_sequence"] = self.tokenizer.stop_token

        return self.environment.from_string(value).render(kwargs)
