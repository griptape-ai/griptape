import logging
import os
import sys
from types import ModuleType
from typing import Any

import pytest

from griptape.utils import import_optional_dependency, is_dependency_installed, optional_type


@pytest.fixture(autouse=True)
def _isolate_optional_type(monkeypatch: pytest.MonkeyPatch):
    """Caches per process, so injected modules must not outlive their test.

    `LoggingConfig`, once any test has built one, sets `propagate = False` and level INFO on the
    "griptape" logger. Both would drop these records before `caplog` sees them, and whether it has
    run yet depends on test order.
    """
    griptape_logger = logging.getLogger("griptape")
    monkeypatch.setattr(griptape_logger, "propagate", True)
    monkeypatch.setattr(griptape_logger, "level", logging.NOTSET)
    optional_type.cache_clear()
    yield
    optional_type.cache_clear()


class TestImportUtils:
    def test_import_optional_dependency(self):
        assert import_optional_dependency("os")
        assert import_optional_dependency("boto3")

        with pytest.raises(ImportError):
            assert import_optional_dependency("foobar")

    def test_is_dependency_installed(self):
        assert is_dependency_installed("os") is True
        assert is_dependency_installed("boto3") is True

        assert is_dependency_installed("foobar") is False

    def test_optional_type(self):
        assert optional_type("boto3") is import_optional_dependency("boto3")
        assert optional_type("os", "getcwd") is os.getcwd

    def test_optional_type_returns_any_for_a_missing_dependency(self, caplog: pytest.LogCaptureFixture):
        """Silently: a plain install without the extras has nothing to report."""
        with caplog.at_level(logging.DEBUG):
            assert optional_type("foobar") is Any
            assert optional_type("foobar", "Client") is Any

        assert caplog.records == []

    def test_optional_type_returns_any_when_the_top_level_import_is_broken(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        """An eager package whose own dependency is broken fails at `import`, not at `getattr`.

        Distinct from absence, and worth reporting: the environment is broken, not unconfigured.
        """

        def raise_broken_transitive(name: str, *_args: object, **_kwargs: object) -> ModuleType:
            if name == "eagerly_broken":
                msg = "cannot import name 'parse_schema' from 'someavro' (unknown location)"
                raise ImportError(msg)
            raise AssertionError(name)

        monkeypatch.setattr("griptape.utils.import_utils.import_module", raise_broken_transitive)

        with caplog.at_level(logging.WARNING):
            assert optional_type("eagerly_broken", "Client") is Any

        assert "eagerly_broken.Client" in caplog.text

    def test_optional_type_returns_any_when_the_attribute_import_fails(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        """A lazy package imports cleanly and only raises on attribute access.

        The failing import is often a broken transitive dependency rather than this package.
        """
        module = ModuleType("lazily_broken")

        def lazy_getattr(name: str) -> Any:
            msg = f"cannot import name 'parse_schema' from 'someavro' (unknown location), wanted for {name}"
            raise ImportError(msg)

        module.__getattr__ = lazy_getattr  # type: ignore[method-assign]
        monkeypatch.setitem(sys.modules, "lazily_broken", module)

        assert optional_type("lazily_broken") is module

        with caplog.at_level(logging.WARNING):
            assert optional_type("lazily_broken", "Client") is Any

        assert "lazily_broken.Client" in caplog.text

    def test_optional_type_returns_any_when_a_transitive_dependency_is_absent(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        """An eager package missing one of its OWN dependencies is broken, not absent.

        The most common real shape, and the one `_is_absent` has to tell apart from the package
        itself being uninstalled.
        """

        def raise_missing_transitive(name: str, *_args: object, **_kwargs: object) -> ModuleType:
            raise ModuleNotFoundError(f"No module named 'fastavro' (imported by {name})", name="fastavro")

        monkeypatch.setattr("griptape.utils.import_utils.import_module", raise_missing_transitive)

        with caplog.at_level(logging.WARNING):
            assert optional_type("eager_pkg", "Client") is Any

        assert "eager_pkg.Client" in caplog.text

    def test_optional_type_returns_any_for_an_empty_directory_on_sys_path(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        """A directory with no `__init__.py` imports as a namespace package with no attributes.

        Indistinguishable from a wrong attribute name except by `__file__`, and it is the shape a
        half-removed install leaves behind.
        """
        husk = ModuleType("husk_pkg")
        husk.__file__ = None
        husk.__path__ = []  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "husk_pkg", husk)

        with caplog.at_level(logging.WARNING):
            assert optional_type("husk_pkg", "Client") is Any

        assert "husk_pkg.Client" in caplog.text

    def test_optional_type_does_not_swallow_a_wrong_attribute_name(self, monkeypatch: pytest.MonkeyPatch):
        """A missing attribute is a caller bug or an upstream rename, not an environment problem.

        Degrading it to `Any` would hide it permanently, since the annotation still resolves. Shaped
        like a real installed package -- both `__file__` and `__path__` -- so that the namespace
        check cannot pass by accident.
        """
        module = ModuleType("present_module")
        module.__file__ = "/somewhere/present_module/__init__.py"
        module.__path__ = ["/somewhere/present_module"]  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "present_module", module)

        with pytest.raises(AttributeError):
            optional_type("present_module", "NoSuchAttribute")
