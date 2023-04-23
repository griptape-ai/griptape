import os
from typing import Optional
from attrs import define, field, Factory
from jinja2 import Environment, FileSystemLoader


@define(frozen=True)
class J2:
    import griptape

    template_name: Optional[str] = field(default=None)
    templates_dir: str = field(default=os.path.join(griptape.core.PACKAGE_ABS_PATH, "resources"), kw_only=True)
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
        return self.environment.get_template(self.template_name).render(kwargs)

    def render_from_string(self, value: str, **kwargs):
        return self.environment.from_string(value).render(kwargs)
