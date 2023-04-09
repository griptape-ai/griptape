import os
from typing import Optional
from attr import define, field, Factory
from jinja2 import Environment, FileSystemLoader
from skatepark.utils import TiktokenTokenizer, Tokenizer
import skatepark


@define(frozen=True)
class J2:
    template_name: Optional[str] = field(default=None)
    templates_dir: str = field(default=os.path.join(skatepark.PACKAGE_ABS_PATH, "templates"), kw_only=True)
    tokenizer: Tokenizer = field(default=TiktokenTokenizer(), kw_only=True)
    environment: Environment = field(
        default=Factory(
            lambda self: Environment(
                loader=FileSystemLoader(self.templates_dir),
                trim_blocks=True,
                lstrip_blocks=True
            ),
            takes_self=True
        ),
        kw_only=True
    )

    def render(self, **kwargs):
        if not kwargs.get("stop_sequence"):
            kwargs["stop_sequence"] = self.tokenizer.stop_sequence

        return self.environment.get_template(self.template_name).render(kwargs)

    def render_from_string(self, value: str, **kwargs):
        if not kwargs.get("stop_sequence"):
            kwargs["stop_sequence"] = self.tokenizer.stop_sequence

        return self.environment.from_string(value).render(kwargs)
