import os
from typing import Optional
from attrs import define, field
from jinja2 import Environment, FileSystemLoader


@define
class J2:
    template: Optional[str] = field()
    templates_path: str = field(default="prompts/templates", kw_only=True)
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
        return self.environment.get_template(self.template).render(kwargs)
