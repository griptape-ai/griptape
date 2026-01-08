from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from .paths import abs_path

if TYPE_CHECKING:
    from jinja2 import Environment


@define(frozen=True)
class J2:
    template_name: Optional[str] = field(default=None)
    templates_dir: str = field(default=abs_path("templates"), kw_only=True)
    environment: Environment = field(
        default=Factory(
            lambda self: self._create_environment(),
            takes_self=True,
        ),
        kw_only=True,
    )

    def _create_environment(self) -> Environment:
        """Lazily import and create a Jinja2 Environment."""
        from jinja2 import Environment, FileSystemLoader

        return Environment(loader=FileSystemLoader(self.templates_dir), trim_blocks=True, lstrip_blocks=True)

    def render(self, **kwargs) -> str:
        if self.template_name is None:
            raise ValueError("template_name is required.")
        return self.environment.get_template(self.template_name).render(kwargs).rstrip()

    def render_from_string(self, value: str, **kwargs) -> str:
        return self.environment.from_string(value).render(kwargs)
