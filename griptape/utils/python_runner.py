from __future__ import annotations

import importlib
import sys
from io import StringIO

from attrs import define, field

from griptape.utils.deprecation import deprecation_warn


@define
class PythonRunner:
    """Runs Python code strings.

    .. deprecated::
        `PythonRunner` is deprecated and will be removed in a future release.
        It does not provide any sandbox isolation — Python's `exec()` automatically
        injects `__builtins__` into any globals dict, including an empty one.
        Never pass untrusted input to this class.
    """

    libs: dict[str, str] = field(factory=dict, kw_only=True)

    def run(self, code: str) -> str:
        deprecation_warn(
            "`PythonRunner` is deprecated and will be removed in a future release. "
            "It does not provide sandbox isolation and must not be used with untrusted input.",
        )
        global_stdout = sys.stdout
        sys.stdout = local_stdout = StringIO()

        try:
            for lib, alias in self.libs.items():
                imported_lib = importlib.import_module(lib)
                globals()[alias] = imported_lib

            exec(f"print({code})", {}, {alias: eval(alias) for alias in self.libs.values()})

            output = local_stdout.getvalue()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = global_stdout

        return output.strip()
