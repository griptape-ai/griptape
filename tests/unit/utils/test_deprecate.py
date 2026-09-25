import sys
from types import ModuleType

import pytest

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.utils.deprecation import DeprecationModuleWrapper, deprecation_warn


class TestDeprecation:
    def test_deprecation_warn(self):
        with pytest.deprecated_call():
            deprecation_warn("This function is deprecated.")

    def test_wrapper_names_the_package_that_re_exports_the_value(self):
        module = ModuleType("legacy")
        module.OpenAiChatPromptDriver = OpenAiChatPromptDriver
        wrapper = DeprecationModuleWrapper(module, "legacy import is deprecated")

        with pytest.warns(DeprecationWarning, match="OpenAiChatPromptDriver") as captured:
            assert wrapper.OpenAiChatPromptDriver is OpenAiChatPromptDriver

        assert str(captured[0].message) == (
            "legacy import is deprecated Use `from griptape.drivers.prompt.openai import OpenAiChatPromptDriver` "
            "instead."
        )

    def test_wrapper_warns_without_a_replacement_for_values_without_a_module(self):
        module = ModuleType("legacy")
        module.value = "plain string"
        wrapper = DeprecationModuleWrapper(module, "legacy import is deprecated")

        with pytest.warns(DeprecationWarning, match="legacy import is deprecated") as captured:
            assert wrapper.value == "plain string"

        assert str(captured[0].message) == "legacy import is deprecated"

    def test_wrapper_warns_without_a_replacement_when_the_parent_package_is_not_imported(self):
        class Detached:
            pass

        Detached.__module__ = "griptape_absent_parent.leaf"
        assert "griptape_absent_parent" not in sys.modules

        module = ModuleType("legacy")
        module.Detached = Detached
        wrapper = DeprecationModuleWrapper(module, "legacy import is deprecated")

        with pytest.warns(DeprecationWarning, match="legacy import is deprecated") as captured:
            assert wrapper.Detached is Detached

        assert str(captured[0].message) == "legacy import is deprecated"

    def test_wrapper_warns_without_a_replacement_when_the_parent_is_the_wrapped_module(self):
        class Leaf:
            pass

        Leaf.__module__ = "legacy_pkg.leaf"

        module = ModuleType("legacy_pkg")
        module.Leaf = Leaf
        wrapper = DeprecationModuleWrapper(module, "legacy import is deprecated")

        sys.modules["legacy_pkg"] = module
        try:
            with pytest.warns(DeprecationWarning, match="legacy import is deprecated") as captured:
                assert wrapper.Leaf is Leaf
        finally:
            del sys.modules["legacy_pkg"]

        assert str(captured[0].message) == "legacy import is deprecated"
