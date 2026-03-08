from __future__ import annotations

import importlib
import sys
from io import StringIO

from attrs import define, field


@define
class PythonRunner:
    """Utility class for running arbitrary Python code.

    WARNING: This class uses `exec()` and `eval()` on input strings and should only be used with trusted input.
    Passing untrusted or LLM-generated code to this class can lead to Arbitrary Code Execution (ACE).
    """

    libs: dict[str, str] = field(factory=dict, kw_only=True)

    def run(self, code: str) -> str:
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
