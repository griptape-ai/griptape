from typing import TYPE_CHECKING
from attrs import define, field, Factory

if TYPE_CHECKING:
    from griptape.utils import J2


@define(slots=False)
class J2Mixin:
    templates_dir: str = field(default=Factory(lambda self: self.abs_path("templates"), takes_self=True), kw_only=True)
    rulesets_template_path: str = field(default="rulesets/rulesets.j2", kw_only=True)
    meta_memory_template_path: str = field(default="memory/meta/meta_memory.j2", kw_only=True)
    user_template_path: str = field(default="user.j2", kw_only=True)
    system_template_path: str = field(default="system.j2", kw_only=True)
    render_args: dict[str, str] = field(default=Factory(dict), kw_only=True)

    def get_template(self, template_name: str) -> "J2":
        from griptape.utils import J2

        return J2(template_name, templates_dir=self.templates_dir)

    def render_template(self, template_name: str, **kwargs) -> str:
        return self.get_template(template_name).render(**self.render_args, **kwargs)

    def render_user_template(self, **kwargs) -> str:
        return self.render_template(self.user_template_path, **kwargs)

    def render_system_template(self, **kwargs) -> str:
        return self.render_template(self.system_template_path, **kwargs)

    def render_rulesets_template(self, **kwargs) -> str:
        return self.render_template(self.rulesets_template_path, **kwargs)

    def render_meta_memory_template(self, **kwargs) -> str:
        return self.render_template(self.meta_memory_template_path, **kwargs)

    def render_from_string(self, template: str, **kwargs) -> str:
        from griptape.utils import J2

        return J2().render_from_string(template, **self.render_args, **kwargs)

    def abs_path(self, path: str) -> str:
        from griptape.utils import abs_path

        return abs_path(path)
