import pytest
from jinja2.exceptions import SecurityError

from griptape.utils import J2


class TestJ2:
    def test_render_from_string(self):
        assert J2().render_from_string("Hello {{ name }}", name="World") == "Hello World"

    def test_render_from_string_expressions(self):
        assert J2().render_from_string("{{ 1 + 1 }}") == "2"
        assert J2().render_from_string("{% for i in items %}{{ i }}{% endfor %}", items=[1, 2, 3]) == "123"
        assert J2().render_from_string("{{ name | upper }}", name="world") == "WORLD"

    def test_render_from_string_public_attrs(self):
        class Foo:
            bar = "baz"

            def qux(self) -> str:
                return "quux"

        assert J2().render_from_string("{{ foo.bar }} {{ foo.qux() }}", foo=Foo()) == "baz quux"

    def test_render_from_string_blocks_unsafe_attrs(self):
        class Foo:
            _bar = "baz"

        # Unsafe attribute access resolves to undefined rather than the value.
        assert J2().render_from_string("{{ foo._bar }}", foo=Foo()) == ""
        assert J2().render_from_string("{{ foo.__class__ }}", foo="bar") == ""

    @pytest.mark.parametrize(
        "template",
        [
            "{{ foo.__class__.__name__ }}",
            "{{ foo.__class__.mro()[1].__subclasses__() }}",
            "{{ cycler.__init__.__globals__['os'].popen('id').read() }}",
        ],
    )
    def test_render_from_string_blocks_code_execution(self, template):
        with pytest.raises(SecurityError):
            J2().render_from_string(template, foo="bar")

    def test_render(self):
        assert J2("memory/conversation/summary.j2").render(summary="foo") == "Summary of the conversation so far: foo"

    def test_render_no_template_name(self):
        with pytest.raises(ValueError, match="template_name is required."):
            J2().render()
