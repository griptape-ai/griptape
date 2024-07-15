from __future__ import annotations

from typing import Optional

from attrs import Factory, define, field
from jinja2 import Environment, FileSystemLoader

from .paths import abs_path


@define(frozen=True)
class J2:
    template_name: Optional[str] = field(default=None)
    templates_dir: str = field(default=abs_path("templates"), kw_only=True)
    environment: Environment = field(
        default=Factory(
            lambda self: Environment(loader=FileSystemLoader(self.templates_dir), trim_blocks=True, lstrip_blocks=True),
            takes_self=True,
        ),
        kw_only=True,
    )

    def render(self, **kwargs) -> str:
        if self.template_name is None:
            raise ValueError("template_name is required.")
        else:
            return self.environment.get_template(self.template_name).render(kwargs).rstrip()

    def render_from_string(self, value: str, **kwargs) -> str:
        return self.environment.from_string(value).render(kwargs)
